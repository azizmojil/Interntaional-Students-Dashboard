# International Students Dashboard 🎓

A comprehensive Business Intelligence (BI) dashboard built with Python's Streamlit framework for analyzing and visualizing international student data.

## Features

- 📊 **Interactive Visualizations**: Multiple charts and graphs using Plotly
- 🔍 **Advanced Filtering**: Filter by country, program, status, gender, and GPA
- 📈 **Multiple Analytics Views**:
  - Overview: General statistics and distributions
  - Geographic Analysis: Country and university distributions
  - Academic Performance: GPA analysis and age distributions
  - Data Table: Searchable and downloadable student data
- 📥 **Data Export**: Download filtered data as CSV
- 🎨 **Responsive Design**: Clean and modern UI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/azizmojil/Interntaional-Students-Dashboard.git
cd Interntaional-Students-Dashboard
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The dashboard will open automatically in your default web browser at `http://localhost:8501`

## Dashboard Sections

### 📈 Overview
- Total students, active students, and graduation statistics
- Distribution by program, status, and gender
- Enrollment trends over time

### 🌍 Geographic Analysis
- Top countries by student count
- University distribution
- Country-wise statistics with average GPA

### 📊 Academic Performance
- GPA distribution histogram
- Average GPA by program and country
- Age distribution analysis

### 📋 Data Table
- Searchable student records
- Sortable columns
- Export functionality

## Data Structure

The dashboard now reads the provided Excel source (`data/data.xlsx`) and normalizes it inside the app. Key input fields include:
- `STD_ID`, `STD_NAME`, `GENDER`
- `CITZ_DESC` (nationality) → mapped to country names
- `MAJR_DESC`, `COLL_DESC`, `LEVL_DESC`
- `STD_GPA`, `STD_HRS`
- `LAST_STST` (detailed status) → grouped into concise status buckets
- `CELG_CODE` (internal/external scholarship)
- `TERM_ADMIT`, `LAST_TERM` (hijri terms converted to approximate Gregorian years for trend lines)

Derived columns such as `country`, `program`, `college`, `status`, `gpa`, and `timeline_year` are created during load time to power the visualizations and filters.

## Technologies Used

- **Streamlit**: Web framework for the dashboard
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computations

## Requirements

See `requirements.txt` for full list of dependencies:
- streamlit==1.31.0
- pandas==2.2.0
- plotly==5.18.0
- numpy==1.26.3

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.
