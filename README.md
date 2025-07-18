# Data Research Engineer

An intelligent PDF research and analysis platform that automatically finds, downloads, and extracts tables from research papers based on your topics of interest.

## ✨ Features

### 🔍 Automated Research
- **Topic-based PDF Discovery**: Simply enter a research topic and let the system find relevant PDFs
- **Smart Search**: Uses multiple search strategies to find academic papers, reports, and research documents
- **Automatic Download**: Downloads found PDFs automatically for processing

### 📊 Advanced PDF Processing
- **Table Extraction**: Automatically extracts tables from PDFs using multiple methods
- **Smart Analysis**: Categorizes and analyzes extracted data
- **Quality Scoring**: Evaluates the quality of extracted tables
- **Multiple Formats**: Supports various table formats and layouts

### 🎯 User-Friendly Interface
- **Modern Sidebar Design**: Clean research interface with progress tracking
- **Real-time Progress**: Live updates during research and processing
- **Manual Upload**: Option to upload your own PDFs for analysis
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### 1. Setup and Installation

```bash
# Clone the repository
git clone https://github.com/ozzy2438/Data-Research-Engineer.git
cd Data-Research-Engineer

# Run the setup script
./run_server.sh
```

### 2. Access the Application

1. **Backend API**: http://localhost:8000
2. **Frontend**: Open `frontend/index.html` in your browser

### 3. Start Researching

1. Enter your research topic in the sidebar (e.g., "machine learning trends 2024")
2. Select how many PDFs to find (3-10)
3. Click "Start Research"
4. Watch as the system finds, downloads, and processes relevant PDFs
5. View extracted tables and analysis results

## 📁 Project Structure

```
Data-Research-Engineer/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── research_service.py  # PDF discovery service
│   ├── pdf_processor.py     # PDF table extraction
│   ├── file_manager.py      # File management utilities
│   ├── websocket_handler.py # Real-time updates
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html          # Main application interface
│   ├── js/app.js           # Frontend JavaScript
│   └── css/styles.css      # Application styling
└── run_server.sh           # Quick setup script
```

## 🔧 Technical Details

### Backend (FastAPI)
- **Async Processing**: Non-blocking PDF processing with progress updates
- **Multi-source Search**: Searches multiple academic databases and repositories
- **Smart PDF Detection**: Identifies and validates PDF documents
- **Table Extraction Pipeline**: Uses advanced algorithms for table detection

### Frontend (Vanilla JavaScript)
- **Modern ES6+**: Clean, maintainable JavaScript code
- **Responsive CSS Grid**: Flexible layout that adapts to screen size
- **Real-time Updates**: Live progress tracking and result display
- **Component-based Design**: Modular and reusable UI components

### Research Process Flow

1. **Query Generation**: Creates multiple search variations for your topic
2. **PDF Discovery**: Searches academic sites, repositories, and databases
3. **Content Validation**: Verifies PDFs are accessible and contain data
4. **Download & Processing**: Downloads PDFs and extracts table content
5. **Analysis & Categorization**: Analyzes and categorizes extracted data
6. **Results Display**: Presents findings in an organized, searchable format

## 📊 Supported PDF Sources

- Academic repositories (arXiv, ResearchGate, IEEE, ACM)
- University publications (.edu domains)
- Government reports and studies
- Industry research and whitepapers
- Conference proceedings and journals

## 🎛️ API Endpoints

### Research Endpoints
- `POST /research/start` - Start automated research
- `GET /research/status/{job_id}` - Get research progress
- `POST /pdf/upload` - Upload manual PDF
- `GET /pdf/status/{job_id}` - Get processing status

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

## 💡 Usage Examples

### Research Topics That Work Well
- "machine learning in healthcare 2024"
- "climate change economic impact"
- "artificial intelligence ethics"
- "renewable energy efficiency"
- "blockchain security analysis"

### Tips for Better Results
1. **Be Specific**: More specific topics yield better, more relevant results
2. **Include Year**: Adding years helps find recent research
3. **Use Academic Terms**: Terms like "study", "analysis", "research" help
4. **Multiple Keywords**: Topics with 3-5 keywords work best

## 🛠️ Development

### Adding New Search Sources
1. Extend `research_service.py` with new search methods
2. Add source-specific PDF detection patterns
3. Update validation logic for new content types

### Customizing Table Extraction
1. Modify `pdf_processor.py` configuration
2. Add new extraction methods or fine-tune existing ones
3. Customize analysis and categorization rules

### Frontend Customization
1. Update `styles.css` for visual changes
2. Extend `app.js` for new functionality
3. Modify `index.html` for layout changes

## 📈 Performance Notes

- **Concurrent Processing**: Multiple PDFs processed in parallel
- **Async Operations**: Non-blocking I/O for better responsiveness
- **Caching**: Smart caching to avoid re-downloading PDFs
- **Error Handling**: Graceful degradation when PDFs can't be processed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. See LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

**"No PDFs found"**
- Try more general search terms
- Check your internet connection
- Some topics may have limited available research

**"Processing failed"**
- PDF might be image-based (scanned) rather than text-based
- Large PDFs may take longer to process
- Some PDFs have complex layouts that are harder to extract

**"Server not starting"**
- Ensure Python 3.8+ is installed
- Check that all dependencies installed correctly
- Verify port 8000 is not in use

### Getting Help

1. Check the console logs in both browser and terminal
2. Verify all dependencies are installed
3. Try with a simple, well-known research topic first
4. Open an issue on GitHub with error details

---

Built with ❤️ for researchers, analysts, and data enthusiasts. 