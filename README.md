# GPUStack UI v2.2.0-dev

A modern, production-ready AI chat interface for GPUStack with advanced authentication, performance monitoring, and intelligent file processing.

## ✨ Features

### Core Functionality
- 💬 **AI Chat Interface** with streaming responses and stop functionality
- 📁 **Enhanced File Processing** - PDF, DOCX, TXT, images with intelligent parsing
- 🔍 **Web Search Integration** via Tavily API
- 🎨 **Modern UI** with dark/light themes and responsive design

### Export/Import System
- 📄 **Markdown Export** - Human-readable format with proper headers
- 📝 **Plain Text Export** - Universal compatibility
- 🔧 **JSON Export** - Complete data fidelity for technical users
- 📥 **Multi-format Import** - Auto-detects and parses different file types

### Performance & Monitoring
- ⚡ **Response Metrics** - Real-time timing and token count tracking
- 🏥 **Health Monitoring** - System status and resource usage
- 🔄 **Async Backend** - Improved concurrency with connection pooling
- 🛑 **Stream Control** - Stop long-running responses

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
git clone https://github.com/your-username/gpustack-ui.git
cd gpustack-ui
git checkout v2.0.0
./setup.sh
```

### Option 2: Docker Compose
```bash
git clone https://github.com/your-username/gpustack-ui.git
cd gpustack-ui
git checkout v2.0.0
cp .env.example .env
# Edit .env with your GPUStack server URL
docker-compose up -d
```

## 📖 Complete Documentation

For detailed deployment instructions, troubleshooting, and advanced configuration:

**[📋 DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide

## 🛠️ Prerequisites

- **Docker & Docker Compose** (recommended)
- **GPUStack server** running and accessible
- **Tavily API key** (optional, for web search)

## ⚙️ Configuration

### Environment Configuration
Optional `.env` file configuration (API keys managed via settings system):
```env
# Environment
ENV=development

# JWT Authentication (optional)
JWT_SECRET_KEY=your-secret-key

# Backend Configuration
BACKEND_PORT=8001
WORKERS=3

# Note: GPUStack and Tavily APIs are configured via the backend settings system
```

### Frontend Configuration
Update `frontend/public/config.js`:
```javascript
window.CONFIG = {
    BACKEND_URL: 'http://localhost:8001'  // or your server IP
};
```

## 🎯 Usage

### Chat Interface
- Start conversations with AI models
- Stream responses with real-time metrics
- Stop long responses with the stop button
- Switch between available models

### File Processing
- Upload PDF, DOCX, TXT, or image files
- Get intelligent content extraction and metadata
- Ask questions about uploaded documents

### Web Search
- Search current information with Tavily integration
- Get AI-summarized search results with sources
- Combine search results with chat conversations

### Export/Import
- Export conversations in Markdown, Text, or JSON
- Import previous conversations from any supported format
- Share conversations easily with colleagues

## 🔗 API Endpoints

### Chat & Inference
- `POST /api/inference/stream` - Streaming chat responses
- `POST /api/inference/infer` - Direct inference
- `GET /api/models` - Available models

### File & Tools
- `POST /api/files/upload` - Enhanced file processing
- `POST /api/tools/search` - AI-powered web search

### Monitoring
- `GET /health` - Health check and system metrics
- `GET /` - API status

## 🚀 What's New in v2.0.0

### Major Enhancements
- **Multi-format Export/Import** - Markdown, Text, JSON support
- **Enhanced File Processing** - Intelligent parsing with metadata
- **Performance Metrics** - Real-time response timing and token counts
- **Stop Chat Functionality** - Interrupt long-running responses
- **Async Backend** - Improved concurrency and connection pooling

### UI/UX Improvements
- **Dropdown Export Menu** - Easy format selection
- **Response Metrics Display** - Performance monitoring in chat
- **Better File Status** - Enhanced upload feedback
- **Improved Error Handling** - Better user feedback

## 🆙 Upgrading from v1.x

v2.0.0 is backward compatible - just pull the latest code and rebuild:
```bash
git pull
git checkout v2.0.0
docker-compose build --no-cache
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request to the `dev-improvements` branch

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/gpustack-ui/issues)
- **Docs**: Check `DEPLOYMENT.md` for detailed setup instructions
- **Logs**: Use `docker-compose logs` for troubleshooting

## 📄 License

[Add your license information here]

---

**GPUStack UI v2.0.0** - Built for enhanced AI interactions with intelligent file processing and flexible conversation management.

