import streamlit as st
from streamlit_extras.stoggle import stoggle
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
import time
from fpdf import FPDF
import base64

class CataractCNN(nn.Module):
    def __init__(self):
        super(CataractCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 28 * 28, 512)
        self.fc2 = nn.Linear(512, 2)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.pool(self.relu(self.conv3(x)))
        x = x.view(-1, 64 * 28 * 28)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

def local_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #FCF6F5;
        }
        
        body {
            color: #990011;
            font-family: 'Source Sans Pro', sans-serif;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #990011, #800010);
            padding: 2rem 1rem;
            color: #FCF6F5;
        }
        
        .sidebar-content {
            padding: 1.5rem;
            color: #FCF6F5;
        }
        
        .sidebar-content h3 {
            color: #FCF6F5;
            border-bottom: 2px solid #FCF6F5;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        
       .main { 
            background: #FCF6F5; 
            padding: 2rem; 
        }
        
        .header {
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #990011, #800010);
            color: #FCF6F5;
            border-radius: 30px;
            margin-bottom: 3rem;
            box-shadow: 0 15px 30px rgba(153,0,17,0.3);
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
            opacity: 0.3;
        }
        
        .header h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #990011, #800010) !important;
            color: #FCF6F5 !important;
            padding: 2rem !important;
            border-radius: 25px !important;
            border: none !important;
            font-size: 1.3rem !important;
            width: 100% !important;
            height: 180px !important;
            margin: 1rem 0 !important;
            transition: all 0.4s ease !important;
            box-shadow: 0 10px 20px rgba(153,0,17,0.2) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-8px) !important;
            box-shadow: 0 15px 30px rgba(129,88,84,0.4) !important;
        }
        
        .toast-notification {
            position: fixed;
            bottom: 20px !important;  /* Changed from top to bottom */
            right: 20px;
            padding: 1rem 2rem;
            border-radius: 10px;
            background: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideIn 0.5s ease-out;
            max-width: 300px;
            border-left: 4px solid #815854;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        .report-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(153,0,17,0.1);
            margin: 20px 0;
            border: 1px solid rgba(153,0,17,0.2);
        }
        
        .report-header {
            border-bottom: 2px solid #990011;
            padding-bottom: 15px;
            margin-bottom: 20px;
            text-align: center;
            color: #990011;
        }
        
        .report-header h2 {
            color: #990011;
            margin: 0;
            font-size: 24px;
        }
        
        .report-section {
            margin: 15px 0;
            padding: 15px;
            background: rgba(153,0,17,0.02);
            border-radius: 5px;
        }
        
        .report-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 15px 0;
        }
        
        .report-item {
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #990011;
        }
        
        .report-label {
            font-weight: bold;
            color: #990011;
        }
        
        .report-value {
            margin-top: 5px;
            color: #333;
        }
        
        .report-recommendations {
            margin-top: 20px;
            padding: 15px;
            background: rgba(153,0,17,0.05);
            border-radius: 5px;
        }
        
        .report-footer {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid rgba(153,0,17,0.2);
            text-align: center;
            font-size: 12px;
            color: #666;
        }
        
        .download-button {
            background: #990011 !important;
            color: white !important;
            padding: 10px 20px !important;
            border-radius: 5px !important;
            border: none !important;
            cursor: pointer !important;
            text-align: center !important;
            margin: 20px auto !important;
            display: block !important;
        }
        
      
        .disclaimer {
            background: rgba(153,0,17,0.05);
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            font-size: 0.9rem;
            color: #990011;
            border-left: 3px solid #990011;
        }
        
        </style>
    """, unsafe_allow_html=True)

def show_toast(message, type="info"):
    colors = {
        "info": "#815854",
        "warning": "#ffc107",
        "error": "#dc3545",
        "success": "#28a745"
    }
    
    st.markdown(f"""
        <div class="toast-notification" style="background: {colors[type]}; color: white">
            <p style="margin: 0;">{message}</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    st.rerun()

def is_image_blurry(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance < 60

def check_lighting(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    mean_brightness = np.mean(gray)
    if mean_brightness < 50:
        return "too_dark"
    elif mean_brightness > 200:
        return "too_bright"
    return "good"

def get_recommendations(prediction):
    if prediction == "Infected":
        return [
            "Schedule an appointment with an ophthalmologist as soon as possible",
            "Avoid driving or operating heavy machinery until evaluated",
            "Protect your eyes from bright light using sunglasses",
            "Keep track of any changes in your vision",
            "Consider starting eye exercises as recommended by your doctor"
        ]
    else:
        return [
            "Continue regular eye check-ups",
            "Maintain a healthy diet rich in vitamins A, C, and E",
            "Protect your eyes from UV radiation",
            "Take regular breaks when using digital devices",
            "Stay hydrated and maintain good eye hygiene"
        ]

def process_image(image, mode='direct'):
    # Check image quality
    if is_image_blurry(image):
        show_toast("⚠️ The image appears to be blurry. Please try taking a clearer photo.", "warning")
        return None, None, None
    
    lighting = check_lighting(image)
    if lighting == "too_dark":
        show_toast("🌑 The environment is too dark. Please ensure better lighting.", "error")
        return None, None, None
    elif lighting == "too_bright":
        show_toast("☀️ The environment is too bright. Please reduce the lighting.", "error")
        return None, None, None
    
    if mode == 'opencv':
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)
        
        predictions = []
        confidence_scores = []
        for (x, y, w, h) in eyes:
            eye_roi = opencv_image[y:y+h, x:x+w]
            eye_pil = Image.fromarray(cv2.cvtColor(eye_roi, cv2.COLOR_BGR2RGB))
            prediction, confidence = get_prediction(eye_pil)
            predictions.append(prediction)
            confidence_scores.append(confidence)
            color = (0, 255, 0) if prediction == 'Normal' else (0, 0, 255)
            cv2.rectangle(opencv_image, (x, y), (x+w, y+h), color, 2)
            cv2.putText(opencv_image, f"{prediction} ({confidence:.1f}%)", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB), predictions, confidence_scores
    else:
        image = image.resize((224, 224))
        prediction, confidence = get_prediction(image)
        return np.array(image), [prediction], [confidence]

def get_prediction(image):
    input_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
        return ('Infected' if predicted.item() == 1 else 'Normal', confidence.item() * 100)

def display_results(image, predictions, confidence_scores):
    # Create a container for the entire report
    report_container = st.container()
    
    with report_container:
        st.markdown("""
            <div class="report-main-header">
                <h1>Eye Analysis Report</h1>
                <p class="report-timestamp">Generated on: {}</p>
            </div>
        """.format(datetime.now().strftime("%B %d, %Y at %I:%M %p")), unsafe_allow_html=True)

        # Report Summary Section
        st.markdown("""
            <div class="report-section summary-section">
                <h2>Report Summary</h2>
                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="summary-label">Report ID</span>
                        <span class="summary-value">{}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Analysis Date</span>
                        <span class="summary-value">{}</span>
                    </div>
                </div>
            </div>
        """.format(
            datetime.now().strftime("%Y%m%d%H%M%S"),
            datetime.now().strftime("%B %d, %Y %I:%M %p")
        ), unsafe_allow_html=True)

        # Key Metrics Section
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div class="metric-card">
                    <h3>Eyes Analyzed</h3>
                    <div class="metric-value">{}</div>
                </div>
            """.format(len(predictions)), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="metric-card">
                    <h3>Confidence</h3>
                    <div class="metric-value">{:.1f}%</div>
                </div>
            """.format(np.mean(confidence_scores)), unsafe_allow_html=True)
        
        with col3:
            status = "Alert" if "Yes" in predictions else "Normal"
            status_color = "#FF4444" if status == "Yes" else "#44BB44"
            st.markdown("""
                <div class="metric-card">
                    <h3>Cataract Status</h3>
                    <div class="metric-value" style="color: {}">{}</div>
                </div>
            """.format(status_color, status), unsafe_allow_html=True)

        # Detailed Analysis Section
        st.markdown("""
            <div class="report-section analysis-section">
                <h2>Detailed Analysis</h2>
                <div class="analysis-details">
                    <div class="analysis-item">
                        <h3>Primary Diagnosis</h3>
                        <p>{}</p>
                    </div>
                    <div class="analysis-item">
                        <h3>Confidence Analysis</h3>
                        <p>The AI model's confidence level indicates {}</p>
                    </div>
                </div>
            </div>
        """.format(
            "Potential cataract detected" if "Infected" in predictions else "No cataract detected",
            "high certainty" if np.mean(confidence_scores) > 90 else "moderate certainty" if np.mean(confidence_scores) > 70 else "further verification needed"
        ), unsafe_allow_html=True)

        # Recommendations Section
        recommendations = get_recommendations('Infected' if 'Infected' in predictions else 'Normal')
        rec_html = "".join([f"<li>{rec}</li>" for rec in recommendations])
        
        st.markdown("""
            <div class="report-section recommendations-section">
                <h2>Recommendations</h2>
                <ul class="recommendations-list">
                    {}
                </ul>
            </div>
        """.format(rec_html), unsafe_allow_html=True)

        # Next Steps Section
        st.markdown("""
            <div class="report-section next-steps-section">
                <h2>Next Steps</h2>
                <div class="next-steps-grid">
                    <div class="next-step-item">
                        <h4>📋 Schedule Follow-up</h4>
                        <p>Book an appointment with an eye care professional for comprehensive evaluation.</p>
                    </div>
                    <div class="next-step-item">
                        <h4>📱 Monitor Changes</h4>
                        <p>Keep track of any vision changes and maintain regular check-ups.</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Footer with disclaimer
        st.markdown("""
            <div class="report-footer">
                <p class="disclaimer-text">⚠️ This report is generated by AI and should be verified by a healthcare professional.</p>
                <p class="copyright-text">© {} EyeCare AI Assistant. All rights reserved.</p>
            </div>
        """.format(datetime.now().year), unsafe_allow_html=True)

        # Add styles for the new report layout
        st.markdown("""
        <style>
            .report-main-header {
                text-align: center;
                padding: 2rem;
                background: linear-gradient(135deg, #990011, #800010);
                color: white;
                border-radius: 15px;
                margin-bottom: 2rem;
            }
            
            .report-section {
                background: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 1.5rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin-top: 1rem;
            }
            
            .summary-item {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .summary-label {
                font-size: 0.9rem;
                color: #666;
            }
            
            .summary-value {
                font-size: 1.1rem;
                font-weight: bold;
                color: #990011;
            }
            
            .metric-card {
                background: white;
                padding: 1.5rem;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            
            .metric-card h3 {
                color: #666;
                font-size: 1rem;
                margin-bottom: 0.5rem;
            }
            
            .metric-value {
                font-size: 1.5rem;
                font-weight: bold;
                color: #990011;
            }
            
            .analysis-details {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
            }
            
            .recommendations-list {
                list-style-type: none;
                padding: 0;
            }
            
            .recommendations-list li {
                padding: 0.8rem;
                margin: 0.5rem 0;
                background: rgba(153, 0, 17, 0.05);
                border-radius: 8px;
                border-left: 3px solid #990011;
            }
            
            .next-steps-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
            }
            
            .next-step-item {
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 10px;
                border: 1px solid #dee2e6;
            }
            
            .report-footer {
                text-align: center;
                margin-top: 3rem;
                padding-top: 1.5rem;
                border-top: 1px solid #dee2e6;
            }
            
            .disclaimer-text {
                color: #666;
                font-size: 0.9rem;
                margin-bottom: 0.5rem;
            }
            
            .copyright-text {
                color: #999;
                font-size: 0.8rem;
            }
        </style>
        """, unsafe_allow_html=True)

        # Create PDF report and download button
        try:
            pdf = create_pdf_report(image, predictions, confidence_scores)
            pdf_output = pdf.output(dest='S').encode('latin-1')
            b64_pdf = base64.b64encode(pdf_output).decode()
            
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_output,
                file_name=f"eye_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
                mime="application/pdf",
                key="download_report"
            )
        except Exception as e:
            st.error("Error generating PDF report. Please try again.")
            print(f"PDF generation error: {str(e)}")

def create_sidebar():
    with st.sidebar:
        st.markdown("### 👁️ EyeCare AI Assistant", unsafe_allow_html=True)
        st.write("Advanced cataract detection powered by artificial intelligence")
        
        st.markdown("### 📋 How to Use", unsafe_allow_html=True)
        st.markdown("""
        1. Choose between taking a photo or uploading an image
        2. Ensure good lighting and clear focus
        3. Keep your eyes centered in the frame
        4. Wait for the AI analysis
        5. Review your detailed report
        """)
        
        st.markdown("### ✨ Best Practices", unsafe_allow_html=True)
        st.markdown("""
        - Use natural lighting when possible
        - Avoid shadows on your face
        - Keep steady while taking photos
        - Ensure both eyes are visible
        """)
        
        st.markdown("### 📞 Contact Us", unsafe_allow_html=True)
        
        contact_col1, contact_col2 = st.columns(2)
        with contact_col1:
            st.markdown("📧 Email")
            st.markdown("📞 Phone")
        with contact_col2:
            st.markdown("nitya.pillai@s.amity.edu")
            st.markdown("9050506090")
            

def show_disclaimer():
    st.markdown("""
        <div class="disclaimer">
            ⚠️ This is a screening tool only and not a substitute for professional medical advice. 
            Results should be verified by a qualified healthcare professional. 
            Regular check-ups are essential. Seek immediate care for severe symptoms.
        </div>
    """, unsafe_allow_html=True)
    
def create_pdf_report(image, predictions, confidence_scores):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'EyeCare AI Diagnostic Report', 0, 1, 'C')
    pdf.ln(5)
    
    # Report ID and Date
    pdf.set_font('Arial', '', 10)
    report_id = datetime.now().strftime("%Y%m%d%H%M%S")
    pdf.cell(0, 10, f'Report ID: {report_id}', 0, 1)
    pdf.cell(0, 10, f'Date: {datetime.now().strftime("%B %d, %Y %I:%M %p")}', 0, 1)
    pdf.ln(5)
    
    # Save the processed image temporarily and add to PDF
    temp_img_path = "temp_processed_image.png"
    cv2.imwrite(temp_img_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    pdf.image(temp_img_path, x=10, w=190)
    import os
    os.remove(temp_img_path)
    
    # Analysis Results
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Analysis Results', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    pdf.cell(95, 10, f'Eyes Analyzed: {len(predictions)}', 1)
    pdf.cell(95, 10, f'AI Confidence: {np.mean(confidence_scores):.1f}%', 1, 1)
    pdf.cell(95, 10, f'Cataract Detection: {predictions.count("Infected")}', 1)
    pdf.cell(95, 10, f'Status: {"Alert" if "Infected" in predictions else "Normal"}', 1, 1)
    
    # Recommendations
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Recommendations', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    recommendations = get_recommendations('Infected' if 'Infected' in predictions else 'Normal')
    for rec in recommendations:
        pdf.cell(0, 10, f'- {rec}', 0, 1)  # Using hyphen instead of bullet point
    
    # Footer
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, 'This report is generated by AI and should be verified by a healthcare professional.', 0, 1, 'C')
    
    return pdf


def main():
    local_css()
    create_sidebar()
    
    st.markdown("""
        <div class="header">
            <h1>🔍 EyeCare AI Assistant</h1>
            <p>Advanced Cataract Detection System</p>
            <div style="font-size: 0.9rem; margin-top: 1rem; opacity: 0.8">
                Powered by Advanced Computer Vision & Machine Learning
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if 'mode' not in st.session_state:
        st.session_state.mode = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📸 Take Photo"):
            st.session_state.mode = 'camera'
            show_toast("Camera activated! Please ensure good lighting and clear focus.", "info")
            
    with col2:
        if st.button("📁 Upload Image"):
            st.session_state.mode = 'upload'
            show_toast("Please select a clear, well-lit image.", "info")
    
    if st.session_state.mode == 'camera':
        picture = st.camera_input("Take a picture")
        if picture:
            image = Image.open(picture)
            processed_image, predictions, confidence_scores = process_image(image, 'opencv')
            if processed_image is not None:
                st.image(processed_image, use_container_width=True)
                display_results(processed_image, predictions, confidence_scores)
                show_toast("Analysis complete! Review your report below.", "success")
            
    elif st.session_state.mode == 'upload':
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            processed_image, predictions, confidence_scores = process_image(image)
            if processed_image is not None:
                st.image(processed_image, use_container_width=True)
                display_results(processed_image, predictions, confidence_scores)
                show_toast("Analysis complete! Review your report below.", "success")
    
    # Show disclaimer only at the bottom of the page
    if not st.session_state.mode:
        show_disclaimer()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CataractCNN().to(device)
model.load_state_dict(torch.load(r"C:\Users\Nitya\Downloads\Eye Disease Detection\cataract.pth", map_location=device))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

if __name__ == "__main__":
    main()