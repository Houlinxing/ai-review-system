# AI Review System

多平台评论聚合分析工具。输入关键词，自动抓取 YouTube / B站相关视频的评论，做情感分析并生成 AI 总结，帮助做购买 / 观看决策。

## 技术栈

**Backend** Python · FastAPI · SQLAlchemy · PostgreSQL
**Frontend** React · Vite · Recharts
**NLP** [xlm-roberta](https://huggingface.co/cardiffnlp/twitter-xlm-roberta-base-sentiment)（本地推理，中英文）
**LLM** NVIDIA API (MiniMax)

## 功能

- YouTube / B站关键词搜索 + 评论抓取（B站基于 WBI 签名，绕过反爬）
- 多语言情感分析，批量本地推理
- AI 生成结构化总结（推荐结论 / 优缺点 / 建议）
- 情感分布图表、趋势图
- 已抓取话题自动走缓存，不重复请求

## 快速开始

```bash
# backend
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # 填入 API keys
uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm run dev
```

### 环境变量

```env
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/ai_review_db
YOUTUBE_API_KEY=
NVIDIA_API_KEY=
```

## API

| Method | Path | 说明 |
|---|---|---|
| POST | `/crawl/youtube/keyword` | YouTube 关键词抓取 |
| POST | `/crawl/bilibili/keyword` | B站关键词抓取 |
| GET | `/comments?topic=` | 评论列表 |
| GET | `/stats/{topic}` | 情感统计 |
| GET | `/summary/{topic}` | AI 总结 |
| GET | `/trend/{topic}` | 情感趋势 |

## 结构

```
backend/app/
├── crawlers/    # 各平台数据抓取
├── services/    # 清洗、情感分析、AI总结
├── routes.py    # API路由
└── models.py    # 数据模型

frontend/src/
├── components/  # UI组件
└── App.jsx
```

## 测试

```bash
cd backend
pytest tests/ -v
```

## Roadmap

- [x] B站数据源
- [x] 搜索记录
- [ ] Reddit 数据源
- [ ] 语言自动检测
- [ ] Redis 缓存

## License

MIT