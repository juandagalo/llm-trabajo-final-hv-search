# LLM Trabajo Final - HV Search

A Streamlit chat application for LLM-based interactions.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/juandagalo/llm-trabajo-final-hv-search.git
cd llm-trabajo-final-hv-search
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

To start the Streamlit chat application:

```bash
streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Features

- **Interactive Chat Interface**: Clean, intuitive chat UI using Streamlit's built-in chat components
- **Session Management**: Maintains chat history during your session
- **Easy Integration**: Simple integration point for custom LLM logic
- **Responsive Design**: Works well on different screen sizes

## Customization

To integrate your own LLM or processing logic:

1. Open `main.py`
2. Find the `process_user_message()` function
3. Replace the placeholder logic with your custom implementation

Example:
```python
def process_user_message(message: str) -> str:
    # Your custom logic here
    # This could be a call to an LLM API, local model, or any other processing
    response = your_llm_function(message)
    return response
```

## Project Structure

```
llm-trabajo-final-hv-search/
├── main.py              # Main Streamlit application
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request