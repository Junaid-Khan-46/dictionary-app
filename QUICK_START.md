# Quick Start Guide

Get your full-stack application running in 5 minutes!

## 🚀 One-Command Setup

```bash
# Clone and setup everything
git clone <your-repo-url>
cd fullstack-template
npm run setup
```

## ⚡ Start Development

**Terminal 1 - Backend:**
```bash
cd backend
cp .env.example .env
python main_test.py  # Uses in-memory storage for quick testing
```

**Terminal 2 - Frontend:**
```bash
cd frontend
cp .env.example .env
pnpm run dev --host
```

## 🎯 Access Your App

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔑 Demo Login

- **Username**: demo
- **Password**: demo123

## 📝 What You Get

✅ **Home Page** - Beautiful landing page with latest posts  
✅ **Authentication** - Login/Signup with JWT tokens  
✅ **Dashboard** - Admin panel with CRUD operations  
✅ **Real-time Updates** - Changes reflect immediately  
✅ **Responsive Design** - Works on all devices  
✅ **Production Ready** - Environment configuration included  

## 🛠️ Next Steps

1. **Customize**: Update branding, colors, and content
2. **Database**: Set up MongoDB for production
3. **Deploy**: Follow deployment guide in README.md
4. **Extend**: Add new features and pages

## 📚 Need Help?

- Read the full [README.md](README.md)
- Check [API Documentation](http://localhost:8000/docs)
- Review the code structure and comments

**Happy coding! 🎉**

