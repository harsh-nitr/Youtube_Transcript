import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()

# Configure generative AI with API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract video ID from URL
def extract_video_id(youtube_video_url):
    regex_patterns = [
        r"youtube\.com/.*v=([^&]*)",  # Standard URL
        r"youtu\.be/([^\?]*)",       # Shortened URL
        r"youtube\.com/embed/([^\?]*)"  # Embed URL
    ]
    for pattern in regex_patterns:
        match = re.search(pattern, youtube_video_url)
        if match:
            return match.group(1)
    return None  # Return None if no ID is found

# Function to extract transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    video_id = extract_video_id(youtube_video_url)
    if video_id is None:
        st.error("Invalid YouTube URL.")
        return None

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript_text = ""

        if transcript_list:
            transcript = transcript_list.find_generated_transcript(['en'])
            for item in transcript.fetch():
                transcript_text += item['text'] + " "

        if not transcript_text:
            st.error("Transcripts are disabled or unavailable for this video.")
            return None
        return transcript_text

    except Exception as e:
        st.error(f"Failed to retrieve transcript: {str(e)}")
        return None

# Function to generate summary using generative AI
def generate_gemini_content(transcript_text, subject):
    # Define the prompt
    prompt = f"""
    You are a YouTube video summarizer. You will be taking the transcript text
    and summarizing the entire video, providing the important points within 1000 words.
    Please provide the summary of the text given here:
    {transcript_text}
    """

    model = genai.GenerativeModel("gemini-pro")  # Initialize generative model
    response = model.generate_content(prompt)    # Generate content based on prompt
    return response.text  # Return the generated summary

# Streamlit app UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

# Display the YouTube video thumbnail
if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    else:
        st.error("Please enter a valid YouTube link.")

# Button to generate detailed notes
if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, "Summary")  # Generate the summary
        st.markdown("## Detailed Notes:")
        st.write(summary)
