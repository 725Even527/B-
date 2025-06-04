📺 Bilibili 弹幕数据抓取与分析可视化工具

本项目提供从Bilibili视频搜索结果中批量抓取弹幕数据，并进行中文分词、TF-IDF关键词提取、词频统计和情感分析，最终生成交互式的可视化HTML页面展示分析结果。

✨ 项目功能概览

🔍 弹幕数据爬取

根据关键词（如“人工智能”）搜索 Bilibili 视频。
自动提取视频 BV 号和 CID，抓取弹幕数据（XML 格式）。
支持指定最大爬取页数，过滤播放量低于一定值的视频（如10000+播放）。
将弹幕信息保存为结构化 Excel 文件。

📊 数据处理与分析
清洗无效弹幕，去重与长度过滤。
使用 jieba 进行中文分词，加载自定义词典与停用词表。
提取 TF-IDF 关键词。
统计词频并生成 Top20 高频词。
使用预训练模型 uer/roberta-base-finetuned-jd-binary-chinese 进行情感分类。

🌐 可视化展示
生成词云图、词频柱状图等静态图像。
自动生成一个美观、交互性强的 HTML 页面展示分析结果，包含：
高频词柱状图（支持鼠标悬浮）
词云图（PNG/JPG）
TF-IDF 表格（可排序）
情感分析统计图（饼图/条形图）

## 📊 第一部分：弹幕爬取（爬取.py）

该脚本用于从Bilibili自动搜索并下载与指定关键词相关视频的弹幕数据，并保存为 Excel 文件，便于后续分析。

---

### 🔧 功能概述

* 自动搜索关键词相关视频
* 提取视频 BV 号 和 弹幕数据
* 保存为单个或合并的 Excel 文件

---

### 🚀 快速使用指南

#### 1️⃣ 安装依赖（首次使用）

```bash
pip install requests beautifulsoup4 pandas openpyxl
```

#### 2️⃣ 修改关键词

打开脚本顶部，找到这行：

```python
KEYWORD = "Python"
```

将其中的关键词替换为你感兴趣的内容，例如 `"人工智能"`。

#### 3️⃣ 运行脚本

```bash
python 爬取.py
```

#### 4️⃣ 输出文件位置

* 单个视频弹幕：保存在 `danmakus/` 文件夹
* 所有弹幕合并表：保存在 `output/combined_danmakus_all.xlsx`

---

### 📌 注意事项

* 脚本每次运行会抓取多个视频，过程较慢请耐心等待
* 若部分视频无弹幕或受限，脚本会自动跳过

---

如需后续分析与可视化，请继续使用后续脚本进行处理。是否需要我也帮你写“分析脚本”和“可视化脚本”的简洁说明？

📁 输出说明
程序运行后会生成以下文件夹和文件：
```
├── danmakus/
│   ├── danmakus_BVxxxxx.xlsx   # 每个视频的弹幕 Excel 文件
├── output/
│   └── combined_danmakus_all.xlsx  # 所有弹幕合并后的总表
```

你只需关注 `output/combined_danmakus_all.xlsx`，它是后续分析的主要输入文件。

常见问题

| 问题                   | 解决方法                 |
| -------------------- | -------------------- |
| 显示“跳过 BVxxxx：未取到CID” | 该视频可能是付费或受限视频，跳过无影响  |
| 返回非XML，跳过            | 视频可能没有弹幕或格式异常，自动跳过   |
| 无法访问B站               | 确保网络连接正常，没有被防火墙或代理阻断 |
| 文件未生成                | 检查是否有视频弹幕，或是否修改了保存路径 |

🧩 高级可选修改（可跳过）
如果你想保存路径不一样，可以修改：
```python
TMP_DIR = "../danmakus"   # 改成你喜欢的文件夹路径
OUT_DIR = "../output"     # 改成你希望的输出路径
```


---

## 📊 第二部分：弹幕数据分析与处理（分析.py）

本模块将抓取好的弹幕 Excel 文件进行处理分析，生成分词、关键词、词频、情感标签等结果，并输出可视化图表。适合零基础用户逐步理解和修改。

### ✅ 1. 读取与清洗数据

```python
df = pd.read_excel(data_path)
df = df[['内容']].dropna().drop_duplicates()
df = df[df['内容'].astype(str).str.len() >= 4]
```

* 读取合并后的弹幕文件 `combined_danmakus_all.xlsx`
* 清除空值、重复项，过滤长度 < 4 的短弹幕，保留有效数据

---

### ✅ 2. 加载词典与停用词

```python
jieba.load_userdict('./stop_dict/keep_words.txt')
```

* 加载自定义保留词（如专有名词、B站用语）
* 停用词来自多个文件合并，剔除常见无意义词（如“的”、“了”、“啊”）

---

### ✅ 3. 中文分词

```python
df['分词'] = df['内容'].astype(str).map(get_cut_content)
```

* 使用 `jieba.cut()` 分词，保留长度 > 1 的词
* 剔除数字、停用词等噪声
* 结果保存为 `分词结果.xlsx`

---

### ✅ 4. TF-IDF 关键词提取

```python
tfidf_tags = analyse.extract_tags(文本, topK=50, withWeight=True)
```

* 从所有弹幕中提取前 50 个最具代表性的关键词
* 结果保存为 `TF-IDF关键词.csv`

---

### ✅ 5. 词频统计与 Top20 输出

```python
word_counts = Counter(all_words)
```

* 统计所有词语出现的频率
* 输出完整统计与 Top20 词频列表：`词频统计.csv`, `词频Top20.csv`

---

### ✅ 6. 高频词柱状图

```python
plt.bar(top_words_df['word'], top_words_df['count'])
```

* 可视化显示最常出现的前 20 个词
* 输出为 `高频词柱状图.png`

---

### ✅ 7. 词云图

```python
WordCloud().generate_from_frequencies(word_counts)
```

* 基于词频生成形状美观的中文词云
* 输出为 `词云图.jpg`

---

### ✅ 8. 情感分析（正向/负向）

```python
predict_sentiment(text)
```

* 使用预训练模型（`RoBERTa`）对每条弹幕判断情感：正向 / 负向
* 输出文件：`弹幕情感分析结果.csv`，含标签和置信度
* 注意：这一部分会比较吃电脑配置，有能力的可以自行选择使用云算力进行。
---

### 🗂 输出结果文件包括：

* `分词结果.xlsx`
* `TF-IDF关键词.csv`
* `词频统计.csv`、`词频Top20.csv`
* `词云图.jpg`、`高频词柱状图.png`
* `弹幕情感分析结果.csv`

---

## 🌐 第三部分：交互式可视化展示HTML 页面（可视化.py）

本模块使用 `pyecharts` 将前一步生成的词频、关键词和情感分析结果图形化，并输出为可交互的 HTML 页面，方便展示与分享。

---

### ✅ 1. TF-IDF 关键词柱状图

```python
Bar().add_xaxis(...).add_yaxis(...).set_global_opts(...)
```

* 展示 TF-IDF 提取的关键词及其重要性
* 支持鼠标缩放、横轴滚动、悬浮提示等交互操作
* 图表主题风格使用 `macarons`

---

### ✅ 2. 高频词词云图

```python
WordCloud().add(...).set_global_opts(...)
```

* 以词频大小可视化展示关键词热度
* 词频越高，字体越大，便于一眼识别高频词
* 自动适配尺寸与布局，居中展示

---

### ✅ 3. 弹幕情感分析饼图

```python
Pie().add(...).set_series_opts(...)
```

* 统计情感标签中正向与负向的占比
* 自动显示每类占比百分比
* 点击可聚焦每一类别，提升交互性

---

### ✅ 4. 词频Top20柱状图

```python
Bar().add_xaxis(...).add_yaxis(...).set_global_opts(...)
```

* 统计弹幕中最常出现的前 20 个词
* 横轴旋转显示，清晰展示文字
* 图表主题使用 `romantic`，风格更轻快

---

### ✅ 5. 汇总输出 HTML 页面

```python
page = Page(layout=Page.DraggablePageLayout)
page.add(...)
page.render("分析可视化展示.html")
```

* 使用可拖拽的布局组件 `DraggablePageLayout`
* 将多个图表整合到一个页面，方便演示和交互
* 输出文件：`分析可视化展示.html`

---

📁 最终生成的 HTML 文件支持本地或网页打开，鼠标可拖拽、缩放、悬浮查看，适用于研究展示、项目汇报或公众号发布。





