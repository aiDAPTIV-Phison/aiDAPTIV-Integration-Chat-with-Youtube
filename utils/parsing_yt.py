from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
import requests
import re
from typing import Tuple
import os 
# os.environ['REQUESTS_CA_BUNDLE'] = './phison-new.pem'
# os.environ['SSL_CERT_FILE'] = './phison-new.pem'


def extract_video_id(video_url: str) -> str:
    """從YouTube URL提取視頻ID"""
    if "youtube.com/watch?v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    elif "youtube.com/shorts/" in video_url:
        return video_url.split("/shorts/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL")

def get_youtube_title(video_id: str) -> str:
    """獲取YouTube視頻標題"""
    try:
        # 方法1: 嘗試從YouTube頁面獲取標題
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # 使用正則表達式提取標題
            title_match = re.search(r'<title>([^<]+)</title>', response.text)
            if title_match:
                title = title_match.group(1)
                # 清理標題，移除" - YouTube"後綴
                title = title.replace(' - YouTube', '').strip()
                if title and title != "YouTube":
                    return title
    except Exception as e:
        st.warning(f"方法1獲取視頻標題失敗: {e}")
    
    try:
        # 方法2: 嘗試從YouTube API獲取標題
        api_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'title' in data:
                return data['title']
    except Exception as e:
        st.warning(f"方法2獲取視頻標題失敗: {e}")
    
    # 如果所有方法都失敗，返回默認格式
    return f"YouTube Video {video_id}"

def fetch_video_data(video_url: str) -> Tuple[str, str]:
    """獲取YouTube視頻數據"""
    try:
        video_id = extract_video_id(video_url)
        
        # 獲取視頻標題
        title = get_youtube_title(video_id)
        
        # 獲取字幕 
        transcript = None
        transcript_text = ""
        
        try:
            # 嘗試獲取英文字幕
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            transcript_text = " ".join([entry["text"] for entry in transcript])
            st.info("📝 已獲取英文字幕")
        except Exception:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['zh', 'zh-cn', 'zh-tw', 'zh-TW'])
                transcript_text = " ".join([entry["text"] for entry in transcript])
                st.info("📝 已獲取中文字幕")
            except Exception as e2:
                # st.warning(f"中英文字幕不可用: {e2}")
                try:
                    # 如果中英文字幕都不可用，嘗試獲取任何可用的字幕
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    transcript_text = " ".join([entry["text"] for entry in transcript])
                    st.info("📝 已獲取其他語言字幕")
                except Exception as e3:
                    st.warning(f"無法獲取任何字幕: {e2}")
                    raise Exception(f"無法獲取任何字幕: {e3}")
        
        return title, transcript_text
    except Exception as e:
        st.error(f"Error fetching video data: {e}")
        return "Unknown", "No transcript available for this video."

