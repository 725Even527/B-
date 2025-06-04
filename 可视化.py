from pyecharts.charts import Bar, Pie, WordCloud, Page
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import pandas as pd
import os

# === 加载数据 ===
tfidf_df = pd.read_csv("TF-IDF关键词.csv")
wordcount_df = pd.read_csv("词频统计.csv")
sentiment_df = pd.read_csv("弹幕情感分析结果.csv")
top20_df = pd.read_csv("词频Top20.csv")

# === 1. TF-IDF 条形图 ===
bar_tfidf = (
    Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="1000px"))
    .add_xaxis(tfidf_df['word'].tolist())
    .add_yaxis("TF-IDF", [round(v, 3) for v in tfidf_df['tfidf']])
    .set_global_opts(
        title_opts=opts.TitleOpts(title="TF-IDF 关键词", pos_left="center", title_textstyle_opts=opts.TextStyleOpts(font_size=20)),
        xaxis_opts=opts.AxisOpts(axislabel_opts={"rotate": 45}),
        datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
    )
)

# === 2. 高频词词云图 ===
wordcloud = (
    WordCloud(init_opts=opts.InitOpts(width="1000px", height="600px"))
    .add("", list(zip(wordcount_df['word'], wordcount_df['count'])))
    .set_global_opts(title_opts=opts.TitleOpts(title="词频词云图", pos_left="center"))
)

# === 3. 情感分析饼图 ===
sentiment_counts = sentiment_df['情感标签'].value_counts()
pie = (
    Pie(init_opts=opts.InitOpts(width="1000px"))
    .add(
        "情感分布",
        [list(z) for z in zip(sentiment_counts.index.tolist(), sentiment_counts.values.tolist())],
        radius=["30%", "60%"]
    )
    .set_global_opts(title_opts=opts.TitleOpts(title="弹幕情感分析", pos_left="center"))
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {d}%"))
)

# === 4. 词频Top20柱状图 ===
bar_top20 = (
    Bar(init_opts=opts.InitOpts(theme=ThemeType.ROMANTIC, width="1000px"))
    .add_xaxis(top20_df['word'].tolist())
    .add_yaxis("词频", top20_df['count'].tolist(), category_gap="30%")
    .set_global_opts(
        title_opts=opts.TitleOpts(title="词频Top20", pos_left="center"),
        xaxis_opts=opts.AxisOpts(axislabel_opts={"rotate": 45}),
        datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
    )
)

# === 5. 汇总到页面 ===
page = Page(page_title="B站弹幕分析报告", layout=Page.DraggablePageLayout)
page.add(bar_tfidf, wordcloud, pie, bar_top20)
page.render("分析可视化展示.html")

print("✅ 成功生成 HTML 页面：分析可视化展示.html")
