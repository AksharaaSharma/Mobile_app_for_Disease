import streamlit as st
import base64
from pathlib import Path

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'quiz_responses' not in st.session_state:
    st.session_state.quiz_responses = []
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False

# Page configuration
st.set_page_config(
    page_title="✨ Eye Disease Detection",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with modern Gen Z aesthetic
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        
        /* Main Styles */
        .main-title {
            font-size: 72px;
            font-weight: 800;
            text-align: center;
            margin: 50px 0;
            background: linear-gradient(120deg, #FF78C4, #7B2CBF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: -2px;
            padding: 20px;
        }
        
        .sub-title {
            color: #2D0040;
            font-size: 36px;
            text-align: center;
            margin: 30px 0;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            letter-spacing: -1px;
        }
        
        /* Modern Container Styles */
        .content-container {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        /* Aesthetic Button Styles */
        .stButton>button {
            width: 100%;
            height: 90px;
            font-size: 26px;
            font-weight: 600;
            margin: 15px 0;
            background: linear-gradient(135deg, #FF78C4, #7B2CBF);
            color: white;
            border-radius: 25px;
            border: none;
            box-shadow: 0 10px 25px rgba(123, 44, 191, 0.3);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: -0.5px;
        }
        
        .stButton>button:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 35px rgba(123, 44, 191, 0.4);
        }
        
        .back-button>button {
            width: 200px !important;
            height: 60px !important;
            font-size: 20px !important;
            background: linear-gradient(135deg, #7B2CBF, #5A189A) !important;
            margin: 20px 0 40px 0 !important;
        }
        
        /* Modern Quiz Card Styles */
        .quiz-card {
            background: white;
            padding: 35px;
            border-radius: 30px;
            box-shadow: 0 10px 30px rgba(123, 44, 191, 0.1);
            margin: 30px 0;
            transition: transform 0.3s ease;
            border: 1px solid rgba(123, 44, 191, 0.1);
        }
        
        .quiz-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(123, 44, 191, 0.15);
        }
        
        .quiz-question {
            font-size: 26px;
            color: #2D0040;
            margin-bottom: 25px;
            padding: 25px;
            background: linear-gradient(to right, #FFE5F1, #F3E8FF);
            border-radius: 20px;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 500;
        }
        
        /* Custom Radio Buttons */
        div.row-widget.stRadio > div {
            background: white;
            padding: 15px;
            border-radius: 15px;
            display: flex;
            gap: 20px;
            justify-content: center;
            box-shadow: 0 5px 15px rgba(123, 44, 191, 0.1);
        }
        
        .stRadio > label {
            font-size: 22px;
            font-weight: 500;
            color: #2D0040;
            font-family: 'Space Grotesk', sans-serif;
        }
        
        /* Result Card Styling */
        .result-card {
            background: linear-gradient(135deg, #FFE5F1, #F3E8FF);
            padding: 40px;
            border-radius: 30px;
            margin-top: 30px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(123, 44, 191, 0.15);
            border: 1px solid rgba(123, 44, 191, 0.1);
        }
        
        /* Progress Bar Styling */
        .stProgress > div > div {
            background-color: #FF78C4;
        }
        
        .stProgress {
            height: 20px;
        }
        
        /* Hide Streamlit Elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Background Gradient */
        .stApp {
            background: linear-gradient(135deg, #FFE5F1 0%, #F3E8FF 100%);
        }
        
        /* Emoji Animations */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        
        .floating-emoji {
            animation: float 3s ease-in-out infinite;
            display: inline-block;
        }
    </style>
""", unsafe_allow_html=True)

# Quiz questions remain the same
quiz_questions = [
    {
        "question": "Do your eyes feel itchy and irritated? ✨",
        "type": "conjunctivitis"
    },
    {
        "question": "Is your vision becoming increasingly cloudy or blurry? 👀",
        "type": "cataract"
    },
    {
        "question": "Do you experience sticky discharge from your eyes? 💧",
        "type": "conjunctivitis"
    },
    {
        "question": "Do you see halos or glare around lights at night? 🌟",
        "type": "cataract"
    },
    {
        "question": "Are your eyes more sensitive to bright light than usual? ⚡",
        "type": "both"
    },
    {
        "question": "Do colors appear faded or less vibrant? 🎨",
        "type": "cataract"
    },
    {
        "question": "Do you wake up with crusty or sticky eyelashes? 👁️",
        "type": "conjunctivitis"
    },
    {
        "question": "Do you need more light than before when reading? 📖",
        "type": "cataract"
    },
    {
        "question": "Is there redness in the white part of your eyes? 🔴",
        "type": "conjunctivitis"
    },
    {
        "question": "Do you find yourself blinking more than usual to clear your vision? ✨",
        "type": "both"
    }
]

def calculate_result():
    cataract_score = 0
    conjunctivitis_score = 0
    
    for response, question in zip(st.session_state.quiz_responses, quiz_questions):
        if response == "Yes":
            if question['type'] == 'cataract':
                cataract_score += 1
            elif question['type'] == 'conjunctivitis':
                conjunctivitis_score += 1
            else:  # type is 'both'
                cataract_score += 0.5
                conjunctivitis_score += 0.5
    
    return cataract_score, conjunctivitis_score

def quiz_page():
    st.markdown('<h2 class="sub-title">✨ Symptoms Quiz ✨</h2>', unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; font-size: 24px; margin-bottom: 40px; color: #2D0040; font-family: "Space Grotesk", sans-serif;'>
            Take this quick quiz to help identify which eye condition you might have! 🌟
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress = len([r for r in st.session_state.quiz_responses if r is not None]) / len(quiz_questions)
    st.progress(progress)
    
    for i, question in enumerate(quiz_questions):
        with st.container():
            st.markdown(f"""
                <div class="quiz-card">
                    <div class="quiz-question">{question["question"]}</div>
                </div>
            """, unsafe_allow_html=True)
            
            response = st.radio(
                f"Question {i+1}",
                options=["Select an option ✨", "Yes ✅", "No ❌"],
                key=f"q{i}",
                label_visibility="collapsed"
            )
            
            if i == len(st.session_state.quiz_responses):
                st.session_state.quiz_responses.append(response if response != "Select an option ✨" else None)
            elif response != "Select an option ✨":
                st.session_state.quiz_responses[i] = "Yes" if response == "Yes ✅" else "No"

    # Submit button
    if all(response is not None for response in st.session_state.quiz_responses):
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("✨ Get Your Results ✨"):
                st.session_state.quiz_completed = True
                cataract_score, conjunctivitis_score = calculate_result()
                
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                if cataract_score > conjunctivitis_score:
                    st.markdown("### 🔍 Based on your symptoms...")
                    st.markdown("""
                        <div style='font-size: 28px; margin: 20px 0; font-family: "Space Grotesk", sans-serif; color: #2D0040;'>
                            You may want to take the <span style='color: #FF78C4; font-weight: bold;'>Cataract Detection</span> test ✨
                        </div>
                    """, unsafe_allow_html=True)
                elif conjunctivitis_score > cataract_score:
                    st.markdown("### 🔍 Based on your symptoms...")
                    st.markdown("""
                        <div style='font-size: 28px; margin: 20px 0; font-family: "Space Grotesk", sans-serif; color: #2D0040;'>
                            You may want to take the <span style='color: #7B2CBF; font-weight: bold;'>Conjunctivitis Detection</span> test ✨
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("### 🤔 Interesting results...")
                    st.markdown("""
                        <div style='font-size: 28px; margin: 20px 0; font-family: "Space Grotesk", sans-serif; color: #2D0040;'>
                            Your symptoms could indicate either condition. We recommend taking both tests! ✨
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# Main page content
if st.session_state.page == 'home':
    st.markdown('<h1 class="main-title">👁️ Eye Disease Detection</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown("""
            <div style='text-align: center; font-size: 28px; margin-bottom: 50px; color: #2D0040; font-family: "Space Grotesk", sans-serif;'>
                Not sure which test you need? Start with our quick symptoms quiz! ✨
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Take Symptoms Quiz ✨"):
            st.session_state.page = "quiz"
            st.rerun()
        
        st.markdown("""
            <div style='text-align: center; margin: 30px 0; color: #2D0040; font-size: 24px; font-family: "Space Grotesk", sans-serif;'>
                - or go directly to -
            </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔍 Cataract Test"):
                st.session_state.page = "cataract_detect"
                st.rerun()
        with col_b:
            if st.button("👁️ Conjunctivitis Test"):
                st.session_state.page = "conjunctivitis_detect"
                st.rerun()

elif st.session_state.page == "quiz":
    st.markdown('<div class="back-button">', unsafe_allow_html=True)
    if st.button('← Back to Home'):
        st.session_state.page = 'home'
        st.session_state.quiz_responses = []
        st.session_state.quiz_completed = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    quiz_page()

elif st.session_state.page == "cataract_detect":
    # Back button
    st.markdown('<div class="back-button">', unsafe_allow_html=True)
    if st.button('← Back to Home'):
        st.session_state.page = 'home'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load cataract detection page
    exec(open(r"C:\Users\Nitya\Downloads\Eye Disease Detection\Cataract App.py", encoding="utf-8").read())

elif st.session_state.page == "conjunctivitis_detect":
    # Back button
    st.markdown('<div class="back-button">', unsafe_allow_html=True)
    if st.button('← Back to Home'):
        st.session_state.page = 'home'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load conjunctivitis detection page
    exec(open(r"C:\Users\Nitya\Downloads\Eye Disease Detection\aksharatry1.py", encoding="utf-8").read())