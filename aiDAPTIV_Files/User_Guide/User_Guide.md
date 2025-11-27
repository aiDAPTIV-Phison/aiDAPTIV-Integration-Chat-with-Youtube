# Chat with YouTube Videos User Guide

## Overview
This application allows users to store video content in the KV Cache, enabling them to select specific videos for QA interactions. This functionality achieves quick responses from the LLM, enhancing the overall user experience.

---
## Chapter 1: Installation and Setting

### Installation Steps

```bash
git clone <repository-url>
cd aiDAPTIV-Integration-Chat-with-Youtube
```
```bash
uv venv
uv pip install -r requirements.txt
```

---

## Chapter 2: How to Use?

### Usage Workflow

1. **Initial Setup**
- Click on `app.exe` to launch the chat interface. The chat room will be automatically opened at http://localhost:8501 (default). 
![image](img/fig_1.PNG)

2. **Basic Operation**
- Fill in the **LLM Endpoint** and **Model Name** as required.
![image](img/fig_2.PNG)

- Paste the YouTube video link to extract the video transcript (default is to prioritize extracting 'en', if unavailable then 'zh'). Successfully added videos will be displayed below.
![image](img/fig_3.PNG)

- Choose the video you want to add to the conversation and start asking questions.
![image](img/fig_4.PNG)
