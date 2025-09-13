import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DeepSeekAPI:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key not found. Please set DEEPSEEK_API_KEY in your .env file")
        
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {str(e)}")
        
    def generate_organized_prompt(self, raw_text, target_use_case="general", programming_language=None, framework=None, expertise_level=None, 
                                 max_tokens=1000, temperature=0.7, top_p=0.9, frequency_penalty=0, presence_penalty=0,
                                 app_name="my-web-app", platform="web", language="en", timezone="UTC", user_id="user-001", user_role="developer"):
        """
        Convert raw text into an organized JSON prompt using DeepSeek API with comprehensive format
        """
        import json
        import uuid
        
        # Generate conversation ID
        conversation_id = str(uuid.uuid4())[:8]
        
        # Create system prompt based on use case for processing the raw text
        if target_use_case == "coding/programming" and programming_language:
            processing_system_prompt = f"You are an expert {programming_language} developer"
            if framework and framework != "None":
                processing_system_prompt += f" specialized in {framework}"
            processing_system_prompt += f". Analyze and summarize the following raw text into a clear, structured developer prompt. Focus on technical requirements, coding standards, and provide {expertise_level.lower()}-level guidance."
        else:
            processing_system_prompt = f"You are a helpful AI assistant specialized in {target_use_case}. Analyze and summarize the following raw text into a clear, structured prompt that captures the key requirements and objectives."
        
        # First, process the raw text using DeepSeek API
        try:
            processing_response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": processing_system_prompt},
                    {"role": "user", "content": f"make this raw text into a more concise, well-structured version of json format:\n\n{raw_text}"}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            
            processed_content = processing_response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to process raw text with DeepSeek: {str(e)}")
        
        # Create system prompt for the final JSON structure
        if target_use_case == "coding/programming" and programming_language:
            final_system_content = f"You are an expert {programming_language} developer"
            if framework and framework != "None":
                final_system_content += f" specialized in {framework}"
            final_system_content += f". You provide {expertise_level.lower()}-level guidance, follow coding best practices, and give structured responses with clear explanations."
        else:
            final_system_content = f"You are a helpful AI assistant specialized in {target_use_case}. Follow user instructions carefully, ask clarifying questions if needed, and provide concise and structured responses."
        
        # Create the comprehensive JSON structure with processed content
        prompt_json = {
            "model": "deepseek-chat",
            "messages": [
            {
                "role": "system",
                "content": final_system_content
            },
            {
                "role": "user", 
                "content": processed_content.strip().replace('\n', ' ').replace('  ', ' ')  # Clean and format the processed content
            }
            ],
            "context": {
            "conversation_id": conversation_id,
            "session_metadata": {
                "app": app_name,
                "platform": platform,
                "language": language,
                "timezone": timezone
            },
            "user_profile": {
                "id": user_id,
                "role": user_role,
                "expertise_level": expertise_level.lower() if expertise_level else "intermediate"
            }
            },
            "generation_config": {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
            },
            "response_format": {
            "type": "text",
            "markdown": False,  # Disable markdown for cleaner output
            "structured_output": {
                "enabled": True,
                "schema": {
                "summary": "string",
                "requirements": ["string"],
                "implementation_steps": ["string"]
                }
            }
            },
            "processing_instructions": {
            "remove_markdown": True,
            "clean_formatting": True,
            "concise_output": True
            },
            "safety": {
            "allow_sensitive": False,
            "block_disallowed": True,
            "moderation_level": "standard"
            }
        }
        
        # Add coding-specific context if applicable
        if target_use_case == "coding/programming" and programming_language:
            prompt_json["context"]["coding_context"] = {
                "programming_language": programming_language,
                "framework": framework if framework and framework != "None" else None,
                "expertise_level": expertise_level
            }
        
        return json.dumps(prompt_json, indent=2)

def main():
    st.set_page_config(
        page_title="AI API Prompt Generator",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 AI API Prompt Generator")
    st.markdown("Transform your raw text into comprehensive, structured API prompts. The system first processes your raw text with DeepSeek using your configured parameters, then creates a complete API request structure.")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "DeepSeek API Key",
            type="password",
            help="Enter your DeepSeek API key. You can also set it in the .env file"
        )
        
        if api_key:
            os.environ["DEEPSEEK_API_KEY"] = api_key
        
        # Target use case selection
        use_case = st.selectbox(
            "Target Use Case",
            [
                "general",
                "coding/programming",
                "creative writing",
                "data analysis",
                "research",
                "business/professional",
                "educational",
                "technical documentation"
            ],
            help="Select the primary use case for your prompt"
        )
        
        # Additional options for coding use case
        programming_language = None
        framework = None
        expertise_level = None
        
        if use_case == "coding/programming":
            st.markdown("#### 💻 Coding Specifications")
            
            # Programming Language dropdown
            programming_language = st.selectbox(
                "Programming Language",
                [
                    "Python",
                    "JavaScript",
                    "TypeScript", 
                    "Java",
                    "C++",
                    "C#",
                    "Go",
                    "Rust",
                    "Swift",
                    "Kotlin",
                    "PHP",
                    "Ruby",
                    "C",
                    "Scala",
                    "R",
                    "MATLAB",
                    "SQL",
                    "HTML/CSS",
                    "Dart",
                    "Other"
                ],
                help="Select the programming language for your coding task"
            )
            
            # Framework dropdown based on selected language
            framework_options = {
                "Python": ["Django", "Flask", "FastAPI", "Streamlit", "PyTorch", "TensorFlow", "Pandas", "NumPy", "Jupyter", "Kivy (Mobile)", "Other"],
                "JavaScript": ["React", "Vue.js", "Angular", "Node.js", "Express.js", "Next.js", "Nuxt.js", "Svelte", "jQuery", "React Native", "Ionic", "Other"],
                "TypeScript": ["React", "Angular", "Vue.js", "Node.js", "Express.js", "Next.js", "NestJS", "Deno", "React Native", "Ionic", "Other"],
                "Java": ["Spring Boot", "Spring Framework", "Hibernate", "Apache Struts", "JSF", "Maven", "Gradle", "Android SDK", "Other"],
                "C++": ["Qt", "Boost", "FLTK", "wxWidgets", "OpenCV", "Unreal Engine", "Other"],
                "C#": [".NET Core", ".NET Framework", "ASP.NET", "Entity Framework", "Xamarin", "Unity", "WPF", ".NET MAUI", "Other"],
                "Go": ["Gin", "Echo", "Fiber", "Buffalo", "Beego", "Revel", "Other"],
                "Rust": ["Actix-web", "Rocket", "Warp", "Axum", "Tokio", "Serde", "Other"],
                "Swift": ["SwiftUI", "UIKit", "Vapor", "Perfect", "Kitura", "Other"],
                "Kotlin": ["Spring Boot", "Ktor", "Android SDK", "Compose", "Jetpack Compose", "Other"],
                "PHP": ["Laravel", "Symfony", "CodeIgniter", "Zend", "CakePHP", "WordPress", "Other"],
                "Ruby": ["Ruby on Rails", "Sinatra", "Hanami", "Padrino", "Other"],
                "R": ["Shiny", "ggplot2", "dplyr", "tidyverse", "caret", "Other"],
                "SQL": ["MySQL", "PostgreSQL", "SQLite", "SQL Server", "Oracle", "MongoDB", "Other"],
                "HTML/CSS": ["Bootstrap", "Tailwind CSS", "Bulma", "Foundation", "Materialize", "Other"],
                "Dart": ["Flutter", "Flutter Web", "Flutter Desktop", "AngularDart", "Other"]
            }
            
            if programming_language in framework_options:
                framework = st.selectbox(
                    f"{programming_language} Framework/Library",
                    ["None"] + framework_options[programming_language],
                    help=f"Select the framework or library for {programming_language}"
                )
            
            # Expertise Level dropdown
            expertise_level = st.selectbox(
                "Expertise Level",
                [
                    "Beginner",
                    "Intermediate", 
                    "Advanced",
                    "Expert"
                ],
                index=1,  # Default to Intermediate
                help="Select your experience level with this technology"
            )
        
        st.markdown("---")
        st.markdown("#### ⚙️ Generation Configuration")
        
        # Generation parameters
        col_gen1, col_gen2 = st.columns(2)
        with col_gen1:
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=4000,
                value=1000,
                step=100,
                help="Maximum number of tokens to generate"
            )
            
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Controls randomness in output (0.0 = deterministic, 2.0 = very random)"
            )
            
        with col_gen2:
            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=0.9,
                step=0.1,
                help="Controls diversity via nucleus sampling"
            )
            
            frequency_penalty = st.slider(
                "Frequency Penalty",
                min_value=0.0,
                max_value=2.0,
                value=0.0,
                step=0.1,
                help="Penalize frequent tokens"
            )
        
        presence_penalty = st.slider(
            "Presence Penalty",
            min_value=0.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            help="Penalize tokens that have appeared"
        )
        
        st.markdown("---")
        st.markdown("#### 🌐 Session Configuration")
        
        # Session metadata
        col_session1, col_session2 = st.columns(2)
        with col_session1:
            app_name = st.text_input(
                "App Name",
                value="my-web-app",
                help="Name of your application"
            )
            
            platform = st.selectbox(
                "Platform",
                ["web", "mobile", "desktop", "api", "cli"],
                help="Platform where this will be used"
            )
            
        with col_session2:
            language = st.selectbox(
                "Language",
                ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
                help="Interface language"
            )
            
            timezone = st.selectbox(
                "Timezone",
                ["UTC", "Asia/Kolkata", "America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney"],
                help="User timezone"
            )
        
        # User profile
        col_user1, col_user2 = st.columns(2)
        with col_user1:
            user_id = st.text_input(
                "User ID",
                value="user-001",
                help="Unique user identifier"
            )
            
        with col_user2:
            user_role = st.selectbox(
                "User Role",
                ["developer", "designer", "manager", "analyst", "student", "researcher", "other"],
                help="User's primary role"
            )
        
        st.markdown("---")
        st.markdown("### 📝 Tips for Better Prompts")
        st.markdown("""
        - Be specific about what you want
        - Include relevant context
        - Mention the desired output format
        - Specify any constraints or requirements
        - Use clear, simple language
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Input: Raw Text")
        
        # Text input methods
        input_method = st.radio(
            "Choose input method:",
            ["Text Area", "File Upload"],
            horizontal=True
        )
        
        raw_text = ""
        
        if input_method == "Text Area":
            raw_text = st.text_area(
                "Enter your raw text or information:",
                height=400,
                placeholder="Paste your raw text here... The system will first process this text using DeepSeek with your configured parameters, then create a structured API prompt."
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload a text file",
                type=['txt', 'md', 'doc'],
                help="Upload a text file containing your raw information"
            )
            
            if uploaded_file is not None:
                try:
                    raw_text = str(uploaded_file.read(), "utf-8")
                    st.text_area("File content preview:", value=raw_text, height=200, disabled=True)
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        # Generate button
        generate_button = st.button(
            "🚀 Generate API Prompt",
            type="primary",
            use_container_width=True,
            disabled=not raw_text.strip()
        )
    
    with col2:
        st.header("✨ Output: API Prompt")
        
        if generate_button and raw_text.strip():
            try:
                with st.spinner("Processing raw text with DeepSeek and generating API prompt..."):
                    try:
                        deepseek_api = DeepSeekAPI()
                    except ValueError as e:
                        # Handle API key not found error
                        st.error(str(e))
                        st.info("💡 Please make sure to:")
                        st.markdown("""
                        1. Enter your DeepSeek API key in the sidebar, OR
                        2. Set the `DEEPSEEK_API_KEY` in your `.env` file
                        3. Get your API key from [DeepSeek Platform](https://platform.deepseek.com/)
                        """)
                        return
                    
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Step 1/2: Processing raw text with DeepSeek...")
                    progress_bar.progress(30)
                    
                    organized_prompt = deepseek_api.generate_organized_prompt(
                        raw_text, 
                        use_case, 
                        programming_language, 
                        framework, 
                        expertise_level,
                        max_tokens,
                        temperature,
                        top_p,
                        frequency_penalty,
                        presence_penalty,
                        app_name,
                        platform,
                        language,
                        timezone,
                        user_id,
                        user_role
                    )
                    
                    status_text.text("Step 2/2: Generating final API prompt structure...")
                    progress_bar.progress(100)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                
                # Display the organized prompt
                st.success("API Prompt generated successfully!")
                
                # Create a container for the output
                output_container = st.container()
                
                with output_container:
                    st.text_area(
                        "Generated API Prompt:",
                        value=organized_prompt,
                        height=400,
                        help="Copy this processed API prompt and use it with any AI service"
                    )
                    
                    # Copy to clipboard button (using JavaScript)
                    if st.button("📋 Copy to Clipboard", key="copy_btn"):
                        st.write("Prompt copied! (Use Ctrl+C/Cmd+C to copy the text from the text area)")
                    
                    # Download as file
                    st.download_button(
                        label="⬇️ Download as .json",
                        data=organized_prompt,
                        file_name="organized_prompt.json",
                        mime="application/json"
                    )
                    
                    # Analytics
                    st.markdown("---")
                    col_stats1, col_stats2, col_stats3 = st.columns(3)
                    
                    with col_stats1:
                        st.metric("Original Length", f"{len(raw_text)} chars")
                    
                    with col_stats2:
                        st.metric("API JSON Length", f"{len(organized_prompt)} chars")
                    
                    with col_stats3:
                        improvement = len(organized_prompt) / len(raw_text) if len(raw_text) > 0 else 0
                        st.metric("Improvement Ratio", f"{improvement:.1f}x")
                
            except Exception as e:
                st.error(f"Error generating prompt: {str(e)}")
                
                if "API key" in str(e):
                    st.info("💡 Please make sure to:")
                    st.markdown("""
                    1. Enter your DeepSeek API key in the sidebar, OR
                    2. Set the `DEEPSEEK_API_KEY` in your `.env` file
                    3. Get your API key from [DeepSeek Platform](https://platform.deepseek.com/)
                    """)
        
        elif not raw_text.strip():
            st.info("👆 Enter some text in the input area to generate an API prompt")
        
        else:
            st.info("📝 Your API prompt will appear here")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.9em;'>
            Built with ❤️ using Streamlit and DeepSeek API | 
            <a href='https://platform.deepseek.com/' target='_blank'>Get DeepSeek API Key</a>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
