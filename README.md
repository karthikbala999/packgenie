# AppPack AI - Application Packaging Assistant

A specialized AI assistant for application packaging tasks, built with Google's Gemini Pro and Streamlit.

## Features

- Interactive chat interface for packaging-related queries
- Specialized in MSI, App-V, MSIX, and Intune packaging
- Provides code snippets, best practices, and troubleshooting
- Context-aware responses based on conversation history

## Prerequisites

- Python 3.8+
- Google API key with access to Gemini Pro

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```
   Get your API key from: https://aistudio.google.com/app/apikey

## Running the Application

```
streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501`

## Example Queries

- "How do I create a silent MSI installer?"
- "Best practices for packaging .NET applications"
- "Troubleshoot error 1603 during installation"
- "Convert MSI to App-V package"
- "How to package a Java application with dependencies?"

## Note

This application requires an internet connection to access the Google Gemini API.
