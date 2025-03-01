
# College Attendance Analyzer

A Streamlit application that analyzes college attendance PDF reports and helps students plan their attendance strategy.

## 📝 Features

* **PDF Extraction** : Automatically extract attendance data from college ERP PDF reports
* **Current Status Analysis** : View your current attendance percentages for each subject
* **Attendance Planning** :
* Calculate how many more classes you need to attend to reach your target percentage (e.g., 75%)
* Find out how many classes you can safely skip while maintaining your desired attendance
* **Data Visualization** : Visual representation of your attendance data with charts and heatmaps
* **Export Functionality** : Download your complete analysis as an Excel file

## 🚀 Getting Started

### Option 1: Regular Setup

#### Prerequisites

* Python 3.7+
* pip (Python package installer)
* poppler-utils (for PDF processing)

#### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/attendance-analyzer.git
cd attendance-analyzer
```

2. Install system dependencies (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils libpoppler-cpp-dev pkg-config
```

3. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install the required dependencies:

```bash
pip install -r requirements.txt
```

5. Run the Streamlit app:

```bash
streamlit run app.py
```

6. Open your browser and go to [http://localhost:8501](http://localhost:8501)

### Option 2: Docker Setup

#### Prerequisites

* Docker
* Docker Compose

#### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/attendance-analyzer.git
cd attendance-analyzer
```

2. Build and run with Docker Compose:

```bash
docker-compose up -d
```

3. Open your browser and go to [http://localhost:8501](http://localhost:8501)

## 📋 Dependencies

The following Python packages are required:

* streamlit
* pandas
* numpy
* pdfplumber
* openpyxl
* xlsxwriter
* matplotlib
* altair

All dependencies are listed in the `requirements.txt` file.

## 🧰 Project Structure

```
attendance-analyzer/
├── app.py                   # Main Streamlit application
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── run_tests.py             # Script to run all tests
├── utils/
│   ├── __init__.py
│   ├── pdf_extractor.py     # PDF parsing functionality
│   └── attendance_calc.py   # Attendance calculation logic
├── tests/
│   ├── test_pdf_extractor.py  # Tests for PDF extraction
│   └── test_attendance_calc.py  # Tests for attendance calculations
└── examples/                # Example files
    └── sample_attendance.pdf  # Sample attendance PDF for testing
```

## 📊 How It Works

1. **Upload** : Upload your attendance PDF from your college ERP
2. **Analysis** : The app extracts and processes the attendance data
3. **Planning** :

* Set your target attendance percentage (default is 75%)
* View how many more classes you need to attend
* Calculate how many classes you can safely skip

1. **Visualize** : View attendance trends, heatmaps, and predictions
2. **Export** : Download your complete analysis as an Excel file

## 🧪 Testing

Run the tests to ensure everything is working correctly:

```bash
python run_tests.py
```

Or use pytest directly:

```bash
pytest tests/
```

## 🔮 Future Improvements

* Support for more PDF formats from different colleges
* Calendar integration for scheduling classes
* Mobile app version
* Notification system for attendance alerts

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ✉️ Contact

If you have any questions or suggestions, please open an issue or contact [your-email@example.com](mailto:your-email@example.com).
