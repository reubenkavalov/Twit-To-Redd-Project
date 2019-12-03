import streamlit as st
from functions import get_liked_tweets, RedditCategoryPredictor


st.title('SubReddit Suggester')
st.markdown('>This app takes your Twitter handle and suggests subreddits to you based on your liked tweets!')

RedditCategoryPredictor(st.text_input("What is your Twitter handle (@) ?"))



