# FriendKeeper 🤝

Help ADHD individuals track and maintain meaningful friendships with smart reminders and AI-powered conversation starters.

## Features

- 📋 **Friendship Tracker**: Track your friends with customizable contact frequency goals
- 🎯 **Health Dashboard**: Visual indicators show which friendships need attention
- 💬 **AI Talk Starters**: Get personalized conversation ideas based on your interaction history
- 🌍 **7 Languages**: English, Chinese, Japanese, German, French, Korean, Spanish
- 📱 **ADHD-Friendly**: Clean, distraction-free interface with gentle reminders

## Tech Stack

- **Frontend**: React + Vite + TypeScript + TailwindCSS
- **Backend**: Python FastAPI + SQLite
- **AI**: LLM Proxy (GPT-4o-mini)
- **Payments**: Creem
- **Deployment**: Docker + nginx

## Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
# Backend
cd backend && pytest --cov=app

# Frontend
cd frontend && npm run test
```

## Deployment

Deployed to `friend-keeper.demo.densematrix.ai` via GitHub Actions.

Ports:
- Frontend: 30065
- Backend: 30066

## License

MIT
