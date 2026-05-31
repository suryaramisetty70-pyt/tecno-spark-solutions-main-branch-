# Buddy AI Frontend - Web Application

Modern, responsive web UI for Buddy AI Operating System built with Next.js 14, React 18, TypeScript, and Tailwind CSS.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local

# Start development server
npm run dev
```

Visit `http://localhost:3000` - application will auto-reload on changes.

## 📁 Project Structure

```
frontend/
├── app/                      # Next.js app directory
│   ├── layout.tsx           # Root layout with auth provider
│   ├── globals.css          # Global styles
│   ├── login/               # Login page
│   │   └── page.tsx
│   └── dashboard/           # Protected dashboard area
│       ├── layout.tsx       # Dashboard layout with sidebar
│       ├── page.tsx         # Main dashboard
│       ├── workflows/       # Workflows page
│       │   └── page.tsx
│       └── search/          # Search page
│           └── page.tsx
├── lib/                      # Utilities and hooks
│   ├── api-client.ts        # Centralized API client
│   └── auth-context.tsx     # Authentication context
├── public/                   # Static assets
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── next.config.js           # Next.js config
├── tailwind.config.js       # Tailwind config
└── postcss.config.js        # PostCSS config
```

## 🔐 Authentication

### Login Flow
1. User enters email and password on `/login`
2. Credentials sent to backend API
3. Token stored in localStorage and context
4. Redirected to `/dashboard` on success
5. Token automatically attached to all API requests

### Protected Routes
- Dashboard and all sub-pages require authentication
- Unauthenticated users redirected to login
- Token validated on component mount

## 🎨 UI Components

### Layout Components
- **Sidebar Navigation** - Collapsible with menu items
- **Top Bar** - User info and actions
- **Dashboard Grid** - Responsive layout

### Pages
- **Login Page** - Email/password authentication
- **Dashboard** - Overview with metrics and quick actions
- **Workflows** - List and manage workflows
- **Search** - Global search with suggestions

## 🔌 API Integration

### API Client (`lib/api-client.ts`)
Centralized HTTP client with:
- Automatic token attachment
- Error handling
- Request/response typing
- RESTful methods (GET, POST, PUT, DELETE)

### Available Endpoints
```typescript
authAPI.login()          // User authentication
userAPI.getProfile()     // Get user profile
workflowAPI.list()       // List workflows
agentAPI.list()          // List agents
fileAPI.list()           // List files
searchAPI.global()       // Global search
analyticsAPI.getDashboard()  // Dashboard data
```

## 🎯 Key Features

### Implemented
✅ User Authentication (JWT)
✅ Dashboard with metrics
✅ Workflows management
✅ Global search
✅ Responsive design
✅ Dark sidebar navigation
✅ Auto-logout on token expiry
✅ Error handling

### Ready to Implement
- Real-time WebSocket updates
- Advanced search filters
- File upload/download
- Agent management UI
- Analytics dashboard
- Admin panel

## 🛠️ Technology Stack

| Technology | Purpose |
|-----------|---------|
| **Next.js 14** | React framework |
| **React 18** | UI library |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Styling |
| **Zod** | Schema validation |
| **Zustand** | State management (ready) |

## 📦 Dependencies

### Core
- `react`: UI components
- `react-dom`: DOM rendering
- `next`: Framework
- `typescript`: Type checking

### UI & Styling
- `tailwindcss`: Utility CSS
- `class-variance-authority`: Component variants
- `lucide-react`: Icons

### Data & State
- `zod`: Validation
- `zustand`: State management

## 🔄 Development Workflow

### Add New Page
1. Create file in `app/dashboard/[name]/page.tsx`
2. Use `useAuth()` hook for authentication
3. Use API client for data fetching
4. Style with Tailwind classes

### Add New API Integration
1. Add endpoint to `lib/api-client.ts`
2. Create new function in appropriate API group
3. Import and use in component
4. Handle loading/error states

### Add Component
1. Create in `components/` directory
2. Use TypeScript for props
3. Export and import where needed

## 🚀 Production Build

```bash
# Build optimized version
npm run build

# Start production server
npm run start

# Type checking
npm run type-check
```

## 🌐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api/v1` | Backend API URL |
| `NEXT_PUBLIC_APP_NAME` | `Buddy AI` | Application name |
| `NEXT_PUBLIC_APP_VERSION` | `0.1.0` | Version number |

## 🔗 Backend Integration

### Expected Backend URL
```
http://localhost:8000/api/v1
```

### Required Endpoints
- `POST /auth/login` - Authentication
- `GET /users/profile` - User data
- `GET /workflows` - Workflows list
- `POST /search/global` - Search functionality
- `GET /analytics/dashboard` - Dashboard data

## 📱 Responsive Design

- **Mobile**: Full-width layout, collapsible sidebar
- **Tablet**: Optimized grid layout
- **Desktop**: Full sidebar with multi-column layout

## 🐛 Debugging

### Enable Debug Mode
```bash
# Set environment variable
DEBUG=app:* npm run dev
```

### Check API Calls
- Open browser DevTools
- Go to Network tab
- Monitor API requests to backend

### Console Logs
- Check browser console for errors
- Check Next.js terminal for build errors

## 📚 Resources

### Documentation
- [Next.js 14 Docs](https://nextjs.org/docs)
- [React 18 Docs](https://react.dev)
- [TypeScript Docs](https://www.typescriptlang.org/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

### Backend API
- Backend running on http://localhost:8000
- API docs at http://localhost:8000/docs (if enabled)

## ✅ Checklist for New Developers

- [ ] Clone repository
- [ ] Install Node.js 18+
- [ ] Run `npm install`
- [ ] Copy `.env.local.example` to `.env.local`
- [ ] Start backend API on port 8000
- [ ] Run `npm run dev`
- [ ] Visit `http://localhost:3000`
- [ ] Try login with test credentials

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Make changes and test locally
3. Commit: `git commit -m "feat: description"`
4. Push: `git push origin feature/name`
5. Create pull request

## 📄 License

Same as backend - Buddy AI OS

## 🆘 Support

For issues or questions:
1. Check documentation
2. Review API responses
3. Check browser console
4. Check Next.js terminal
5. Contact team

---

**Status**: ✅ Ready for Development
