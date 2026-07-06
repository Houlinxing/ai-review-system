# AI Review System

> 多平台评论舆情分析系统 — 通过关键词聚合社交媒体评论，结合 NLP 情感分析与 LLM 总结，帮助用户快速做出决策。

---

## 项目定位

用户在做决策前（去某个景点、买某款产品）需要参考大量评论，但分散在各平台、语言混杂、信息量大。本系统将这个过程自动化：

```
用户输入关键词
    ↓
系统自动抓取多个相关视频的评论
    ↓
NLP 情感分析 + AI 结构化总结
    ↓
一键得到：该不该去/买 + 优缺点 + 实用建议
```

---

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | React + Vite + Recharts |
| 后端 | FastAPI + Python 3.12 |
| 数据库 | PostgreSQL + SQLAlchemy |
| NLP | HuggingFace Transformers（xlm-roberta） |
| LLM | NVIDIA API（MiniMax M2.7） |
| 数据源 | YouTube Data API v3 |

---

## 功能特性

- **关键词搜索**：输入关键词自动搜索相关视频，聚合多视频评论
- **缓存机制**：已抓取过的关键词直接读取数据库，不重复调用 API
- **多语言情感分析**：支持中文、英文及多语言混合评论
- **批量推理**：本地模型批量处理，无外部 API 依赖，无速率限制
- **AI 结构化总结**：输出推荐结论、优点、缺点、实用建议
- **数据可视化**：情感分布柱状图、比例环形图、趋势折线图
- **去重写入**：相同评论不重复入库（基于 comment_id）
- **暗色模式**：支持亮色/暗色主题切换

---

## 项目结构

```
ai-review-system/
├── backend/
│   └── app/
│       ├── crawlers/
│       │   └── youtube_crawler.py      # YouTube 评论抓取 + 视频搜索
│       ├── services/
│       │   ├── sentiment_service.py    # NLP 情感分析（xlm-roberta）
│       │   ├── ai_service.py           # LLM 结构化总结
│       │   ├── youtube_service.py      # 评论清洗 + 聚合
│       │   └── comment_service.py      # 数据库 CRUD
│       ├── utils/
│       │   └── text_cleaner.py         # 文本清洗（HTML/URL/hashtag）
│       ├── core/
│       │   └── response.py             # 统一响应格式
│       ├── models.py                   # SQLAlchemy 数据模型
│       ├── schemas.py                  # Pydantic 请求/响应模型
│       ├── routes.py                   # FastAPI 路由
│       ├── database.py                 # 数据库连接
│       └── main.py                     # 应用入口
└── frontend/
    └── src/
        ├── components/
        │   ├── SearchBar.jsx
        │   ├── StatsGrid.jsx
        │   ├── SummaryCard.jsx         # AI 结构化总结展示
        │   ├── SentimentChart.jsx      # 柱状图 + 饼图 + 趋势图
        │   └── CommentsList.jsx
        ├── styles/
        │   └── global.css
        └── App.jsx
```

---

## 数据库表结构

```sql
comments
├── id              INTEGER       主键
├── platform        VARCHAR(50)   平台来源（youtube）
├── video_id        VARCHAR(100)  视频 ID
├── comment_id      VARCHAR(150)  评论唯一 ID（去重）
├── topic           VARCHAR(200)  搜索关键词
├── content         TEXT          评论正文（清洗后）
├── language        VARCHAR(20)   评论语言
├── region          VARCHAR(100)  地区（后续平台填充）
├── like_count      INTEGER       点赞数
├── reply_count     INTEGER       回复数
├── sentiment       FLOAT         情感分数（-1.0 ~ 1.0）
├── sentiment_label VARCHAR(20)   positive / negative / neutral
├── published_at    TIMESTAMPTZ   评论发布时间
└── created_at      TIMESTAMPTZ   入库时间
```

---

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/crawl/youtube` | 单视频评论抓取 |
| POST | `/crawl/youtube/keyword` | 关键词搜索抓取（推荐） |
| GET | `/comments?topic=xxx` | 查询评论列表 |
| GET | `/stats/{topic}` | 情感统计数据 |
| GET | `/summary/{topic}` | AI 结构化总结 |
| GET | `/trend/{topic}` | 情感趋势（按时间） |

---

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 安装依赖
pip install fastapi uvicorn sqlalchemy psycopg
pip install transformers torch --index-url https://download.pytorch.org/whl/cu126
pip install sentencepiece tiktoken openai python-dotenv google-api-python-client

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入以下内容

# 启动服务
uvicorn app.main:app --reload
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

---

## 环境变量

在 `backend/.env` 中配置：

```env
# 数据库
DATABASE_URL=postgresql+psycopg://用户名:密码@localhost:5432/ai_review_db

# YouTube Data API v3
YOUTUBE_API_KEY=your_youtube_api_key

# NVIDIA LLM API
NVIDIA_API_KEY=your_nvidia_api_key
```

### 获取 API Key

| Key | 获取地址 |
|---|---|
| YouTube API | [Google Cloud Console](https://console.cloud.google.com/) → 启用 YouTube Data API v3 |
| NVIDIA API | [NVIDIA NGC](https://integrate.api.nvidia.com/) |

---

## 情感分析说明

| 分数范围 | 标签 | 含义 |
|---|---|---|
| > 0.3 | positive | 正面评价 |
| -0.3 ~ 0.3 | neutral | 中性评价 |
| < -0.3 | negative | 负面评价 |

模型：`cardiffnlp/twitter-xlm-roberta-base-sentiment`
- 支持中文、英文及多语言混合
- 本地推理，无外部 API 依赖
- 首次运行自动下载模型（约 1.1GB）

---

## 后续规划

- [ ] langdetect 接入（自动检测评论语言）
- [ ] 模型预热（消除冷启动延迟）
- [ ] Reddit API 接入（第二个数据源）
- [ ] 异步任务队列（长任务后台处理）
- [ ] Redis 缓存层
- [ ] 用户系统（搜索历史、收藏）

---

## License

MIT
