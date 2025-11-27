import streamlit as st
import json
import os
import requests
from datetime import datetime
from utils.parsing_yt import fetch_video_data


st.set_page_config(
    layout="wide"                        # Set layout to wide mode
)

# Initialize session state
if 'video_data' not in st.session_state:
    st.session_state.video_data = []
if 'data_path' not in st.session_state:
    st.session_state.data_path = "./aiDAPTIV_Files/Example/Files/video_data.json"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_video' not in st.session_state:
    st.session_state.selected_video = None
if 'vllm_endpoint' not in st.session_state:
    st.session_state.vllm_endpoint = "http://localhost:13141/v1/chat/completions" # http://10.102.196.26:18302/v1/chat/completions
if 'model_name' not in st.session_state:
    st.session_state.model_name = "Llama-3.2-3B-Instruct-Q4_K_M.gguf" # gpt-oss-20b

def count_tokens(text: str) -> int:
    """Simple token counter (based on character count estimation)"""
    # This is a simplified token count, actual applications may need more precise methods
    return int(len(text.split()) * 1.3)  # Rough estimation

def save_video_data_to_json(video_data: list, file_path: str):
    """Save video data to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Error saving JSON file: {e}")

def load_video_data_from_json(file_path: str) -> list:
    """Load video data from JSON file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return []

def call_vllm_api_streaming(question: str, video_context: str, endpoint: str):
    """Call vLLM API for Q&A with streaming support"""
    try:
        # Prepare the prompt with video context
        system_prompt = """You are a helpful assistant that answers questions based on the provided video transcript. 
        Please answer the user's question using only the information from the video transcript. 
        If the answer cannot be found in the transcript, please say so clearly."""
        
        user_prompt = f"""Video Transcript:
{video_context}

Question: {question}

Please answer the question based on the video transcript above."""

        # Prepare the request payload with streaming enabled
        payload = {
            "model": st.session_state.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": True
        }
        
        # Make the streaming API request
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300,
            stream=True
        )
        
        if response.status_code == 200:
            # Process streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    content = delta['content']

                                    # full_response += content
                                    yield content  # Yield each chunk for real-time display
                        except json.JSONDecodeError:
                            continue
            return full_response
        else:
            yield f"Error calling vLLM API: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        yield f"Error connecting to vLLM endpoint: {str(e)}"
    except Exception as e:
        yield f"Error processing response: {str(e)}"

def call_vllm_api(question: str, video_context: str, endpoint: str) -> str:
    """Call vLLM API for Q&A (non-streaming fallback)"""
    try:
        # Prepare the prompt with video context
        system_prompt = """You are a helpful assistant that answers questions based on the provided video transcript. 
        Please answer the user's question using only the information from the video transcript. 
        If the answer cannot be found in the transcript, please say so clearly."""
        
        user_prompt = f"""Video Transcript:
{video_context}

Question: {question}

Please answer the question based on the video transcript above."""

        # Prepare the request payload
        payload = {
            "model": st.session_state.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Make the API request
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error calling vLLM API: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"Error connecting to vLLM endpoint: {str(e)}"
    except Exception as e:
        return f"Error processing response: {str(e)}"

def simple_qa_search(question: str, video_context: str) -> str:
    """Fallback Q&A search based on keyword matching"""
    question_lower = question.lower()
    context_sentences = video_context.split('.')
    return f"Based on the video content: {video_context}"

def add_to_chat_history(role: str, content: str):
    """Add message to chat history"""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })


# Load existing video data
st.session_state.video_data = load_video_data_from_json(st.session_state.data_path)

# Main content area
st.title("🎥 YouTube Video Chat")
st.write("Welcome to the YouTube Video Chat application!")

# Sidebar for video management
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # vLLM API Configuration
    st.subheader("🤖 LLM API Settings")
    vllm_endpoint = st.text_input(
        "LLM Endpoint", 
        value=st.session_state.vllm_endpoint,
        help="Enter your vLLM API endpoint URL"
    )
    st.session_state.vllm_endpoint = vllm_endpoint
    
    model_name = st.text_input(
        "Model Name", 
        value=st.session_state.model_name,
        help="Enter the model name to use for API calls"
    )
    st.session_state.model_name = model_name
    
    
    st.markdown("---")
    
    st.header("📺 Add YouTube Video")
    video_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("➕ Add Video to Knowledge Base", use_container_width=True):
        if video_url:
            try:
                with st.spinner("Fetching video information..."):
                    title, transcript = fetch_video_data(video_url)
                
                if transcript != "No transcript available for this video.":
                    # Display fetched title
                    st.info(f"📺 **Video Title**: {title}")
                    
                    # Calculate token count
                    token_count = count_tokens(transcript)
                    
                    # Create data structure matching requirements
                    video_entry = {
                        "title": title,
                        "url": video_url,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "context": transcript,
                        "tokens": token_count
                    }
                    
                    # Add to session state
                    st.session_state.video_data.append(video_entry)
                    
                    # Save to JSON file
                    save_video_data_to_json(st.session_state.video_data, st.session_state.data_path)
                    
                    # Call vLLM API
                    if st.session_state.vllm_endpoint:
                        with st.spinner("Processing video content..."):
                            summary_question = "Please provide a brief summary of this video content."
                            call_vllm_api(
                                summary_question,
                                transcript,
                                st.session_state.vllm_endpoint
                            )
                    st.success(f"✅ Added video **'{title}'** to knowledge base! (Tokens: {token_count})")
                else:
                    st.warning(f"⚠️ Video '{title}' has no available subtitles")
            except Exception as e:
                st.error(f"❌ Error adding video: {e}")
        else:
            st.warning("Please enter a YouTube video URL")
    
    # Display added videos list in sidebar
    if st.session_state.video_data:
        st.header("📋 Added Videos")
        for i, video in enumerate(st.session_state.video_data):
            with st.expander(f"{i+1}. {video['title'][:30]}..."):
                st.write(f"**URL**: {video['url']}")
                st.write(f"**Added**: {video['timestamp']}")
                st.write(f"**Tokens**: {video['tokens']}")
                st.write(f"**Preview**: {video['context'][:100]}...")
                
                # Delete button for each video
                if st.button(f"🗑️ Delete", key=f"delete_{i}", help=f"Delete '{video['title'][:30]}...'"):
                    # Remove video from session state
                    st.session_state.video_data.pop(i)
                    # Save updated data to JSON file
                    save_video_data_to_json(st.session_state.video_data, st.session_state.data_path)
                    st.success(f"✅ Deleted video: {video['title'][:30]}...")
                    st.rerun()

# Main content area for chat
st.subheader("💬 Chat with Your Videos")

# Video selection
if st.session_state.video_data:
    video_options = [f"{i+1}. {video['title']}" for i, video in enumerate(st.session_state.video_data)]
    selected_index = st.selectbox(
        "Select a video to chat with:",
        range(len(video_options)),
        format_func=lambda x: video_options[x],
        key="video_selector"
    )
    
    if selected_index is not None:
        st.session_state.selected_video = st.session_state.video_data[selected_index]
        st.info(f"📺 **Selected Video**: {st.session_state.selected_video['title']}")
        
        # Chat interface
        st.markdown("---")
        
        # Display chat history
        if st.session_state.chat_history:
            st.subheader("💬 Chat History")
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"**You** ({message['timestamp']}): {message['content']}")
                else:
                    st.markdown(f"**AI Assistant** ({message['timestamp']}): {message['content']}")
                st.markdown("---")
        
        # Chat input
        user_question = st.text_input("Ask a question about the video:", placeholder="What is this video about?")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("Send", use_container_width=True):
                if user_question and st.session_state.selected_video:
                    # Add user question to chat history
                    add_to_chat_history("user", user_question)
                    
                    # Get answer from video content
                    if st.session_state.vllm_endpoint:
                        # Create a placeholder for streaming response
                        response_placeholder = st.empty()
                        full_response = ""
                        
                        # Stream the response
                        for chunk in call_vllm_api_streaming(
                            user_question, 
                            st.session_state.selected_video['context'],
                            st.session_state.vllm_endpoint
                        ):
                            if chunk:
                                full_response += chunk
                            response_placeholder.markdown(f"**AI Assistant** ({datetime.now().strftime('%H:%M:%S')}): {full_response}")
                        
                        # Add complete response to chat history
                        add_to_chat_history("assistant", full_response)
                    else:
                        # Fallback search
                        answer = simple_qa_search(user_question, st.session_state.selected_video['context'])
                        add_to_chat_history("assistant", answer)
                    
                    # Rerun to update the chat display
                    st.rerun()
        
        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
else:
    st.info("No videos available. Please add some YouTube videos from the sidebar first.")