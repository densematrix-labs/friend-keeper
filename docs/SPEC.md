# FriendKeeper — Mini Spec

## 目标

帮助 ADHD 人群追踪和维护友谊关系，通过可视化和提醒系统确保不会忽略重要的人际关系。

**Target Users**: ADHD 人群、容易忘记联系朋友的人、想要系统性维护社交关系的人

## 核心功能

### 1. 友谊追踪 (Friendship Tracker)
- 添加朋友：姓名、昵称、关系类型（好友/同事/家人等）
- 设置联系频率目标（每周/每两周/每月/每季度）
- 记录最近一次互动时间和内容摘要

### 2. 互动记录 (Interaction Logger)
- 快速记录每次联系（一键"已联系"）
- 可选添加笔记：聊了什么、下次要问的事
- 互动历史时间线

### 3. 友谊健康度仪表盘 (Friendship Health Dashboard)
- 可视化显示每个朋友的"健康度"（基于联系频率 vs 目标）
- 颜色编码：绿色=OK、黄色=快到期、红色=需要联系
- 今日/本周需要联系的朋友列表

### 4. 智能提醒 (Smart Reminders)
- AI 生成个性化联系建议（基于之前的互动笔记）
- "Talk Starters"：根据历史对话生成话题建议

## 技术方案

- **前端**: React + Vite (TypeScript) + TailwindCSS
- **后端**: Python FastAPI
- **数据库**: SQLite
- **AI 调用**: 通过 llm-proxy.densematrix.ai
- **部署**: Docker → langsheng
- **端口**: Frontend 30065, Backend 30066

## 美学方向

**Aesthetic**: Soft Organic / Friendly Minimalism

- **调色板**: 温暖的自然色调 - 米色背景、柔和的绿色和桃色作为强调色
- **字体**: 
  - Display: DM Serif Display (温暖、友好、人文)
  - Body: Plus Jakarta Sans (现代、清晰、易读)
- **特点**: 
  - 圆润的形状和柔和的阴影
  - 大量负空间让 ADHD 用户不感到压迫
  - 可爱但不幼稚的图标系统
  - 动画要平滑但不过度

## 完成标准

- [x] 友谊追踪功能可用
- [x] 互动记录功能可用
- [x] 健康度仪表盘可视化
- [x] AI 话题建议功能
- [x] 支付集成（按次计费）
- [x] 7 种语言支持
- [x] 部署到 friend-keeper.demo.densematrix.ai
- [x] Health check 通过
