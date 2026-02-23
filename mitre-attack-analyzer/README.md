# MITRE ATT&CK Log Analyzer

A full-stack web application for analyzing security logs using AI to detect suspicious activities and map them to MITRE ATT&CK techniques.

## 🏗️ Architecture

- **Frontend**: React 18 + Tailwind CSS + Vite
- **Backend**: Python FastAPI with async MongoDB
- **Database**: MongoDB
- **ML Model**: Qwen2.5-1.5B-Instruct with LoRA fine-tuning
- **Pattern**: Controller-Service-Repository (3-tier architecture)

## 📁 Project Structure

```
mitre-attack-analyzer/
├── backend/
│   ├── app/
│   │   ├── controllers/     # REST API endpoints
│   │   ├── services/        # Business logic & ML
│   │   ├── repositories/    # Database operations
│   │   ├── models/          # MongoDB schemas
│   │   ├── utils/           # Helper functions
│   │   ├── config.py        # Configuration
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/      # React components
    │   ├── services/        # API client
    │   └── App.jsx
    ├── package.json
    └── vite.config.js
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB Atlas account (free tier) OR MongoDB 5.0+ local installation
- 8GB RAM minimum (16GB recommended for ML model)
- Internet connection for downloading base model (first run only)

### Backend Setup

1. **Setup MongoDB**

   **Option A - MongoDB Atlas (Recommended for beginners):**
   - Sign up at https://cloud.mongodb.com
   - Create a free M0 cluster
   - Create database user with password
   - Set Network Access to `0.0.0.0/0` (allow from anywhere)
   - Copy connection string

   **Option B - Local MongoDB:**

   ```powershell
   # Download from: https://www.mongodb.com/try/download/community
   # Or use Docker:
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

2. **Navigate to backend directory**

   ```powershell
   cd backend
   ```

3. **Create virtual environment**

   ```powershell
   python -m venv venv
   ```

4. **Install dependencies**

   ```powershell
   venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   **For GPU Support (Recommended):**

   If you have an NVIDIA GPU, install PyTorch with CUDA support for faster inference:

   ```powershell
   # Uninstall CPU-only PyTorch
   venv\Scripts\python.exe -m pip uninstall torch -y

   # Install PyTorch with CUDA 11.8
   venv\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

   Then set `DEVICE=cuda` in your `.env` file.

5. **Configure environment**

   ```powershell
   # Copy example env file
   cp .env.example .env

   # Edit .env with your settings
   # The model will auto-download from HuggingFace on first run
   ```

6. **Run backend server**

   ```powershell
   # Run using virtual environment Python
   venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

   Backend will be available at: http://localhost:8000
   API docs at: http://localhost:8000/docs

   **First Run**: The server will download the base model (~3GB) and cache it locally. This takes 5-10 minutes.  
   **Subsequent Runs**: Loads from cache in ~30-60 seconds (no re-download).

### Frontend Setup

1. **Navigate to frontend directory**

   ```powershell
   cd frontend
   ```

2. **Install dependencies**

   ```powershell
   npm install
   ```

3. **Run development server**

   ```powershell
   npm run dev
   ```

   Frontend will be available at: http://localhost:3000

## 📖 Usage

1. **Access the web interface** at http://localhost:3000

2. **Upload or paste a JSON log**
   - Click to upload a `.json` file
   - Or paste JSON content directly in the text area

3. **Click "Analyze Log"**
   - The system will analyze the log using the fine-tuned ML model
   - Results will show:
     - Status: Normal/Suspicious/Unknown
     - Reasoning for the classification
     - MITRE ATT&CK techniques (if suspicious)
     - Processing time

4. **View statistics** in the right sidebar
   - Total analyses
   - Status breakdown
   - Suspicious detection rate

## 🔌 API Endpoints

### POST /api/logs/analyze

Analyze a security log

```json
{
  "log_content": "{\"event_id\": 4624, ...}",
  "session_id": "optional-session-id"
}
```

### GET /api/logs/history/{analysis_id}

Get specific analysis result

### GET /api/logs/recent?limit=10

Get recent analyses

### GET /api/logs/stats

Get statistics dashboard data

### GET /api/logs/health

Health check endpoint

Full API documentation: http://localhost:8000/docs

## 🧠 Model Information

- **Base Model**: Qwen/Qwen2.5-1.5B-Instruct
  - Downloads ~3GB on **first run only** (5-10 minutes)
  - Cached locally in: `C:\Users\<YourUsername>\.cache\huggingface\`
  - Subsequent runs load from cache (30-60 seconds)
- **Fine-tuned Adapters**: Loaded from `E:\Hacking\Mitre-Dataset\fine_tuned_model`
- **Technique**: LoRA (Low-Rank Adaptation)
- **Input**: JSON security logs (max 6000 chars)
- **Output**: Status + Reason + MITRE Techniques
- **Startup Time**:
  - First run: ~5-10 minutes (includes download)
  - Subsequent runs: ~30-60 seconds (loads from cache)

## 🔧 Configuration

### Backend (.env)

```env
# Model Configuration
BASE_MODEL=Qwen/Qwen2.5-1.5B-Instruct
MODEL_PATH=E:\Hacking\Mitre-Dataset\fine_tuned_model
DEVICE=cuda  # or cpu

# MongoDB Configuration (use MongoDB Atlas or local)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=mitre_attack_logs

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Model Parameters
MAX_INPUT_CHARS=6000
MAX_LENGTH_TOKENS=4096
MAX_NEW_TOKENS=256
```

### Frontend (vite.config.js)

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

## 🛠️ Development

### Backend Development

```powershell
# Install dev dependencies
pip install black flake8 pytest

# Format code
black app/

# Run tests
pytest
```

### Frontend Development

```powershell
# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 📊 Database Schema

### LogAnalysis Collection

```javascript
{
  _id: ObjectId,
  log_content: String,
  status: "Normal" | "Suspicious" | "Unknown" | "Error",
  reason: String,
  mitre_techniques: [String],
  raw_output: String,
  processing_time: Float,
  session_id: String (optional),
  analyzed_at: DateTime,
  created_at: DateTime,
  updated_at: DateTime
}
```

## 🎯 Features

✅ **AI-Powered Analysis**: Fine-tuned LLM for security log classification
✅ **MITRE Mapping**: Automatic technique identification
✅ **Real-time Processing**: Async backend for fast responses
✅ **Persistent Storage**: MongoDB for analysis history
✅ **Statistics Dashboard**: Track detection metrics
✅ **Modern UI**: Tailwind CSS with responsive design
✅ **Auto-scaling**: Handle large log files
✅ **Session Tracking**: Group related analyses

## 🚨 Troubleshooting

### Backend Issues

**MongoDB connection fails**

- For **MongoDB Atlas (Cloud)**: Check your connection string in `.env` and ensure IP whitelist includes `0.0.0.0/0` in Network Access settings
- For **Local MongoDB**:

  ```powershell
  # Check if MongoDB is running
  Get-Process mongod

  # Start MongoDB service
  net start MongoDB
  ```

**Model download fails**

```powershell
# Manually download model
pip install huggingface_hub
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct')"
```

**Note**: The model is automatically cached in `C:\Users\<YourUsername>\.cache\huggingface\` after first download. Subsequent runs will load from cache (no re-download).

**Slow startup after first run**

The model loads into RAM/GPU memory every time the backend starts (~30-60 seconds). This is normal - it's loading from cache, not downloading again.

**GPU not being used (shows "Using device: cpu")**

1. Check if CUDA is available:

   ```powershell
   venv\Scripts\python.exe -c "import torch; print('CUDA:', torch.cuda.is_available())"
   ```

2. If it says `False`, install PyTorch with CUDA support:

   ```powershell
   venv\Scripts\python.exe -m pip uninstall torch -y
   venv\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. Verify CUDA works:

   ```powershell
   venv\Scripts\python.exe -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
   ```

4. Set `DEVICE=cuda` in `.env` file

**Out of memory errors**

- Reduce MAX_INPUT_CHARS in .env
- Close other applications
- If on CPU, switch to GPU (see above)
- For small GPUs (<8GB): Model uses ~3-4GB with float16
- Clear HuggingFace cache if needed: `rm -Recurse -Force ~\.cache\huggingface\`

### Frontend Issues

**Port 3000 already in use**

```powershell
# Change port in vite.config.js
server: { port: 3001 }
```

**API calls fail**

- Check backend is running on port 8000
- Verify CORS_ORIGINS in backend .env includes frontend URL

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues or questions, please create a GitHub issue.
