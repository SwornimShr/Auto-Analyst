# Auto-Analyst: AI-Powered CSV Analysis Tool

A web-based application that enables users to analyze CSV data through natural language queries. Built with Streamlit and powered by LangChain's pandas agent integration with Groq's Llama-3.3-70B model.

---

## Overview

Auto-Analyst bridges the gap between non-technical users and data analysis by accepting plain English questions and executing corresponding pandas operations automatically. The system handles data loading, query interpretation, code generation, and result presentation without requiring users to write any code.

![Main Interface](screenshots/main-interface.png)
---

## Key Features

- **Natural Language Processing**: Accepts conversational queries including "how many," "what is," and other question formats
- **Automatic CSV Processing**: Handles multiple text encodings (UTF-8, Latin-1, ISO-8859-1, CP1252) with automatic detection
- **Column Normalization**: Standardizes column names to lowercase with underscores for consistent querying
- **Query Pattern Recognition**: Automatically converts informal questions to structured commands
- **Self-Correcting Agent**: Implements retry logic with configurable iteration limits to handle parsing errors
- **Query Analytics**: Tracks success rates and maintains query history for performance monitoring
- **Real-Time Feedback**: Displays query interpretations and provides contextual error messages

   ![Main Interface](screenshots/query-results.png)


---

## Technical Architecture

### Core Components

**app.py** (202 lines)  
Main Streamlit application handling UI rendering, user interaction, and session state management.

**agent.py** (180+ lines)  
LangChain wrapper implementing the pandas DataFrame agent with query normalization and pattern recognition.

**utils.py** (78 lines)  
CSV processing utilities including encoding detection, column normalization, and data validation.

**tracker.py** (58 lines)  
Query logging system for monitoring success rates and maintaining conversation history.

### Technology Stack

- **Frontend**: Streamlit 1.31.0
- **AI Framework**: LangChain 0.1.4, LangChain Experimental 0.0.50
- **LLM Provider**: Groq API (Llama-3.3-70B model)
- **Data Processing**: Pandas 2.1.4
- **Visualization**: Matplotlib 3.8.2, Seaborn 0.13.1

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Groq API key ([obtain here](https://console.groq.com/))

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/auto-analyst.git
   cd auto-analyst
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials**
   
   Create `.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
   
   **Important**: Replace `your-groq-api-key-here` with your actual Groq API key. The application will not function without valid credentials.

5. **Launch application**
   ```bash
   streamlit run app.py
   ```

6. **Access interface**
   
   Navigate to `http://localhost:8501` in your web browser.

![Main Interface](screenshots/app-running.png)
---

## Usage

### Basic Workflow

1. Upload a CSV file using the file browser or drag-and-drop interface
2. Review the data preview and summary statistics
3. Enter queries in natural language format
4. Examine results displayed as tables, metrics, or visualizations

### Query Examples

**Data Exploration:**
```
show all rows
display first 10 rows
show unique values in department column
```

**Aggregations:**
```
calculate the average salary
what is the sum of years_experience
count employees in each department
```

**Filtering:**
```
show rows where salary > 80000
display employees in the Engineering department
filter rows where age is between 30 and 40
```

**Sorting:**
```
sort by salary descending and show first 5 rows
display employees ordered by years_experience
```

**Natural Language Questions:**
```
how many employees in each department
what is the average salary
who has the highest performance_score
```

![Main Interface](screenshots/query-examples.png)
---

## Configuration

### API Model Selection

The default configuration uses Groq's `llama-3.3-70b-versatile` model. To modify the model:

1. Open `agent.py`
2. Locate line 17: `model_name: str = "llama-3.3-70b-versatile"`
3. Replace with an alternative Groq model identifier

Available alternatives include `llama-3.1-8b-instant` for faster responses or other models listed in [Groq's documentation](https://console.groq.com/docs/models).

### Iteration Limits

The agent is configured with `max_iterations=10` to prevent infinite loops. This can be adjusted in `agent.py` at the `create_pandas_dataframe_agent()` call based on query complexity requirements.

---

## Known Limitations

### Display Formatting
Complex queries occasionally return results as plain text rather than formatted tables. The underlying data remains accurate; only the presentation is affected. This is a known limitation of LangChain's pandas agent implementation.

### Query Complexity
Multi-step queries requiring more than 10 iterations may terminate prematurely. Consider breaking complex analyses into sequential simpler queries.

### File Size Constraints
Performance degrades with CSV files exceeding 100MB. For large datasets, consider sampling or using database alternatives.

### Model Availability
The application requires an active internet connection to communicate with Groq's API. Queries will fail if the API is unreachable or if rate limits are exceeded.

---

## Project Structure

```
auto-analyst/
├── app.py                      # Main Streamlit application
├── agent.py                    # LangChain agent wrapper
├── utils.py                    # CSV processing utilities
├── tracker.py                  # Query analytics
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── LICENSE                     # MIT License
├── .gitignore                  # Git exclusions
├── .streamlit/
│   ├── config.toml            # Streamlit configuration
│   └── secrets.toml.template  # API key template
└── sample_data.csv            # Example dataset
```

---

## Development Roadmap

Future enhancements under consideration:

- Excel file format support (.xlsx, .xls)
- Query result export functionality (CSV, JSON formats)
- Persistent query history across sessions
- Multi-file join operations
- Advanced visualization generation
- Database connectivity (PostgreSQL, MySQL)

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes with descriptive messages
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request with a detailed description

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for complete terms.

---

## Citation

If you use this project in academic work, please cite:

```
[Swornim Shrestha]. (2026). Auto-Analyst: AI-Powered CSV Analysis Tool.
GitHub repository: https://github.com/SwornimShr/Auto-Analyst
```

---

**Version**: 2.1    
**Status**: Active Development
