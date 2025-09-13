# AI Prompt Generator 🤖

A Streamlit application that transforms raw text into organized, effective prompts using the DeepSeek API. Perfect for creating structured prompts for ChatGPT, DeepSeek, GitHub Copilot, and other AI assistants.

## Features

- **Text Transformation**: Convert messy, unstructured text into clear, actionable prompts
- **Multiple Input Methods**: Text area input or file upload support
- **Use Case Optimization**: Tailor prompts for different scenarios (coding, creative writing, research, etc.)
- **Export Options**: Copy to clipboard or download as text file
- **Analytics**: View improvement metrics and text statistics
- **User-Friendly Interface**: Clean, responsive Streamlit UI

## Setup

### Option 1: Docker (Recommended)

#### Using Docker Compose

1. **Clone and navigate to the project**:
```bash
cd /Users/akhilk/Desktop/prompter
```

2. **Set up environment variables**:
Create a `.env` file with your DeepSeek API key:
```bash
echo "DEEPSEEK_API_KEY=your_deepseek_api_key_here" > .env
```

3. **Run with Docker Compose**:
```bash
docker-compose up -d
```

4. **Access the application**:
Open your browser and go to `http://localhost:8501`

5. **Stop the application**:
```bash
docker-compose down
```

#### Using Docker directly

1. **Build the image**:
```bash
docker build -t ai-prompt-generator .
```

2. **Run the container**:
```bash
docker run -d \
  --name prompter \
  -p 8501:8501 \
  --env-file .env \
  ai-prompt-generator
```

### Option 2: Local Installation

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Configure API Key

Create a `.env` file in the project root and add your DeepSeek API key:

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

Or enter it directly in the app's sidebar when running.

#### 3. Get DeepSeek API Key

1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Sign up or log in
3. Navigate to API section
4. Generate a new API key
5. Copy the key and add it to your `.env` file

## Usage

### Running the Application

#### With Docker:
```bash
docker-compose up -d
```

#### Locally:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### How to Use

1. **Enter Raw Text**: Paste your unstructured text or upload a file
2. **Select Use Case**: Choose the target application (general, coding, creative writing, etc.)
3. **Configure API**: Enter your DeepSeek API key in the sidebar
4. **Generate Prompt**: Click the "Generate Organized Prompt" button
5. **Copy/Download**: Use the generated prompt with your favorite AI assistant

### Example Use Cases

#### Input (Raw Text):
```
need help with python function that reads files and processes data maybe use pandas also need error handling and should be fast
```

#### Output (Organized Prompt):
```
Please help me create a Python function with the following requirements:

**Objective**: Create a function that reads and processes data files efficiently

**Technical Requirements**:
- Use pandas for data processing
- Implement proper error handling
- Optimize for performance/speed
- Handle file reading operations

**Expected Output**: 
A complete Python function with:
- Clear function signature and parameters
- Error handling for file operations and data processing
- Performance optimizations
- Code comments explaining key parts
- Usage example

Please provide a robust, production-ready solution that follows Python best practices.
```

## Project Structure

```
prompter/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (API key)
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore         # Docker ignore file
└── README.md             # This file
```

## Docker Configuration

### Dockerfile Features
- **Base Image**: Python 3.11 slim for optimal size and security
- **Multi-stage optimization**: Efficient layer caching
- **Non-root user**: Enhanced security
- **Health checks**: Container health monitoring
- **Environment variables**: Proper configuration management

### Docker Compose Features
- **Service orchestration**: Easy deployment and management
- **Environment management**: Automatic .env file loading
- **Network isolation**: Dedicated network for the application
- **Health monitoring**: Built-in health checks
- **Volume management**: Optional persistent storage
- **Auto-restart**: Resilient deployment

## Configuration Options

### Use Cases
- **General**: All-purpose prompt optimization
- **Coding/Programming**: Optimized for development tasks
- **Creative Writing**: Enhanced for creative and content generation
- **Data Analysis**: Structured for analytical tasks
- **Research**: Academic and research-focused prompts
- **Business/Professional**: Corporate and professional contexts
- **Educational**: Learning and teaching scenarios
- **Technical Documentation**: Documentation and technical writing

### Input Methods
- **Text Area**: Direct text input in the browser
- **File Upload**: Upload `.txt`, `.md`, or `.doc` files

## API Integration

The application uses the DeepSeek API with the following configuration:
- **Model**: `deepseek-chat`
- **Temperature**: `0.7` (balanced creativity/consistency)
- **Max Tokens**: `2000` (suitable for detailed prompts)

## Error Handling

The application includes comprehensive error handling for:
- Missing API keys
- Network connectivity issues
- API rate limits
- Invalid file formats
- Empty input validation

## Security

- API keys are handled securely through environment variables
- No sensitive data is logged or stored
- Secure HTTPS communication with DeepSeek API

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Issues**: Verify your DeepSeek API key is valid
   - Check the `.env` file format
   - Ensure no extra spaces or quotes around the key

3. **Network Issues**: Check your internet connection and firewall settings

4. **File Upload Issues**: Ensure uploaded files are in supported formats (txt, md, doc)

5. **Docker Issues**:
   - **Port already in use**: Change the port mapping in docker-compose.yml
     ```yaml
     ports:
       - "8502:8501"  # Use 8502 instead of 8501
     ```
   - **Permission denied**: Ensure Docker has proper permissions
   - **Container won't start**: Check logs with `docker-compose logs prompter`

### Docker Commands

```bash
# View logs
docker-compose logs prompter

# Restart service
docker-compose restart prompter

# Update and rebuild
docker-compose down
docker-compose up --build -d

# Clean up
docker-compose down --volumes --remove-orphans
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
