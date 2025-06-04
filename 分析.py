import os
import pandas as pd
import jieba
from collections import Counter
import itertools
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from wordcloud import WordCloud
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# === 设置路径 ===
base_dir = os.path.dirname(__file__)  # 当前脚本路径
data_path = os.path.join(base_dir, '../output/combined_danmakus_all.xlsx')  # 相对路径读取
output_path = os.path.join(base_dir, '分词结果.xlsx')

# === 1. 读取数据（XLSX） ===
df = pd.read_excel(data_path)
df = df[['内容']].dropna().drop_duplicates()
df = df[df['内容'].astype(str).str.len() >= 4].reset_index(drop=True)
print(f"✅ 读取并清洗数据，共 {len(df)} 条弹幕")

# === 2. 加载用户词典与停用词 ===
jieba.load_userdict('./stop_dict/keep_words.txt')
stopwords = set()
for fname in ['./stop_dict/stopwords_hit.txt', './stop_dict/mystopwords.txt']:
    with open(fname, encoding='utf-8') as f:
        stopwords.update(f.read().splitlines())
stopwords.update([' ', '', '\n', '\t', '\xa0', '\u3000', '�'])

# === 3. 分词 ===
def get_cut_content(text):
    words = jieba.cut(text, cut_all=False, HMM=True)
    return [w for w in words if w not in stopwords and not w.isdigit() and len(w) > 1]

df['分词'] = df['内容'].astype(str).map(get_cut_content)
df['分词文本'] = df['分词'].map(lambda x: ' '.join(x))
df[['分词文本']].to_excel(output_path, index=False)
print("✅ 已保存分词结果")

# === 4. TF-IDF 关键词提取 ===
import jieba.analyse as analyse
tfidf_tags = analyse.extract_tags(' '.join(df['分词文本']), topK=50, withWeight=True)
tfidf_df = pd.DataFrame(tfidf_tags, columns=['word', 'tfidf'])
tfidf_df.to_csv('TF-IDF关键词.csv', index=False, encoding='utf-8-sig')
print("✅ 已保存 TF-IDF 关键词")

# === 5. 词频统计 ===
all_words = list(itertools.chain(*df['分词']))
word_counts = Counter(all_words)
word_counts_df = pd.DataFrame(word_counts.items(), columns=['word', 'count']).sort_values(by='count', ascending=False)
word_counts_df.to_csv('词频统计.csv', index=False, encoding='utf-8-sig')
top_words_df = word_counts_df.head(20)
top_words_df.to_csv('词频Top20.csv', index=False)
print("✅ 已保存词频统计和Top20")

# === 6. 词频柱状图 ===
plt.rcParams["font.sans-serif"] = ['SimHei']
plt.rcParams["axes.unicode_minus"] = False
plt.figure(figsize=(12, 8))
plt.title('高频词统计')
plt.bar(top_words_df['word'], top_words_df['count'])
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('高频词柱状图.png')
plt.show()
print("✅ 已保存高频词柱状图")

# === 7. 词云图 ===
wc = WordCloud(
    background_color='white',
    font_path='C:/Windows/Fonts/simhei.ttf',
    width=1000,
    height=800,
    max_words=300,
    max_font_size=100,
    scale=2
).generate_from_frequencies(word_counts)

plt.figure(figsize=(12, 8))
plt.imshow(wc, interpolation="bilinear")
plt.axis('off')
plt.tight_layout()
plt.savefig('词云图.jpg')
plt.show()
print("✅ 已生成并保存词云图")

# === 8. 情感分析 ===
try:
    print("📦 正在加载情感分析模型...")
    model_name = "uer/roberta-base-finetuned-jd-binary-chinese"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    print("✅ 模型加载完成")

    def predict_sentiment(text):
        if not isinstance(text, str) or text.strip() == "":
            return None, None
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
        return ("positive" if probs[1] >= probs[0] else "negative", float(probs.max()))

    df['情感标签'] = ''
    df['情感置信度'] = 0.0
    for idx, row in df.iterrows():
        label, score = predict_sentiment(row['内容'])
        df.at[idx, '情感标签'] = label
        df.at[idx, '情感置信度'] = score

    df.to_csv("弹幕情感分析结果.csv", index=False, encoding='utf-8-sig')
    print("✅ 情感分析已完成并保存为 弹幕情感分析结果.csv")
except Exception as e:
    print(f"❌ 情感分析失败：{e}")

# === 9. 输出生成的文件 ===
print("\n📁 当前目录下生成的结果文件：")
for f in os.listdir():
    if f.endswith(('.csv', '.xlsx', '.png', '.jpg')):
        print(" -", f)
