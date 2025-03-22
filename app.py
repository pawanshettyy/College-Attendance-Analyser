import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
import altair as alt
import tempfile
import os
import logging
import traceback
from PIL import Image

# Import utility functions
from utils.pdf_extractor import extract_attendance_data
from utils.attendance_calc import (
    calculate_classes_needed,
    calculate_classes_can_miss
)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Streamlit UI
st.set_page_config(
    page_title="College Attendance Analyzer",
    page_icon="📊",
    layout="wide"
)

# App version
APP_VERSION = "1.0.1"

# Cache the attendance data extraction to improve performance
@st.cache_data(ttl=3600, show_spinner=False)
def cached_extract_attendance_data(uploaded_file):
    """Cached version of the attendance data extraction function"""
    try:
        # We need to save the uploaded file to disk temporarily
        # as pdfplumber works better with file paths than file objects
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
            
        # Extract data using the path
        with open(tmp_path, 'rb') as f:
            result = extract_attendance_data(f)
            
        # Clean up the temporary file
        os.unlink(tmp_path)
        return result
    except Exception as e:
        logger.error(f"Error in cached data extraction: {str(e)}")
        logger.debug(traceback.format_exc())
        st.error(f"Error processing PDF: {str(e)}")
        return {
            "student_name": "Unknown",
            "subjects": [],
            "overall": {"Present": 0, "Total": 0, "Percentage": 0}
        }

def create_attendance_heatmap(df):
    """Create a heatmap for attendance visualization"""
    if df.empty:
        st.warning("No data available for visualization")
        return None
        
    try:
        # Prepare data for heatmap
        subjects = df['Subject'].tolist()
        percentages = df['Percentage'].tolist()
        
        # Create a color scale based on percentage
        colors = []
        for percentage in percentages:
            if percentage >= 75:
                colors.append('#4CAF50')  # Green
            elif percentage >= 60:
                colors.append('#FFC107')  # Yellow
            else:
                colors.append('#F44336')  # Red
        
        fig, ax = plt.subplots(figsize=(10, max(3, len(subjects) * 0.4)))
        
        # Create horizontal bars
        y_pos = np.arange(len(subjects))
        ax.barh(y_pos, percentages, color=colors)
        
        # Add percentage labels
        for i, percentage in enumerate(percentages):
            ax.text(percentage + 1, i, f"{percentage:.1f}%", va='center')
        
        # Customize axes
        ax.set_yticks(y_pos)
        ax.set_yticklabels(subjects)
        ax.set_xlabel('Attendance Percentage')
        ax.set_xlim(0, 110)
        
        # Add a reference line at 75%
        ax.axvline(x=75, color='black', linestyle='--', alpha=0.7)
        ax.text(75, len(subjects) + 0.1, '75% Required', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    except Exception as e:
        logger.error(f"Error creating heatmap: {str(e)}")
        st.error("Error creating visualization. Please try again.")
        return None

def create_attendance_trend_prediction(present, total, target=75, future_classes=15):
    """Create a trend chart showing how attendance will change with each class"""
    try:
        # Handle division by zero
        if total == 0:
            st.warning("No attendance data available for prediction")
            return None
            
        # Current percentage
        current_percentage = (present / total) * 100
        
        # Initialize data
        classes = list(range(future_classes + 1))
        attendance_if_present = []
        attendance_if_absent = []
        
        # Calculate percentages for each scenario
        for i in classes:
            # If present in all future classes
            if_present = (present + i) / (total + i) * 100
            attendance_if_present.append(if_present)
            
            # If absent in all future classes
            if_absent = present / (total + i) * 100
            attendance_if_absent.append(if_absent)
        
        # Create dataframe
        df = pd.DataFrame({
            'Classes': classes,
            'If Present': attendance_if_present,
            'If Absent': attendance_if_absent,
            'Target': [target] * len(classes)
        })
        
        # Create chart
        chart = alt.Chart(df).transform_fold(
            ['If Present', 'If Absent', 'Target'],
            as_=['Scenario', 'Percentage']
        ).mark_line().encode(
            x=alt.X('Classes:Q', title='Future Classes'),
            y=alt.Y('Percentage:Q', scale=alt.Scale(domain=[0, 100])),
            color=alt.Color('Scenario:N', 
                            scale=alt.Scale(
                                domain=['If Present', 'If Absent', 'Target'],
                                range=['#4CAF50', '#F44336', '#2196F3']
                            )
                           ),
            strokeDash=alt.condition(
                alt.datum.Scenario == 'Target',
                alt.value([5, 5]),  # dashed line for target
                alt.value([0])  # solid line for others
            )
        ).properties(
            title='Attendance Trend Prediction',
            width=600,
            height=400
        ).interactive()
        
        return chart
    except Exception as e:
        logger.error(f"Error creating trend prediction: {str(e)}")
        st.error("Error creating prediction chart. Please try again.")
        return None

def create_pie_chart(present, total):
    """Create a pie chart showing attendance distribution"""
    try:
        if total == 0:
            st.warning("No data available for visualization")
            return None
            
        absent = total - present
        
        # Data for pie chart
        labels = ['Present', 'Absent']
        sizes = [present, absent]
        colors = ['#4CAF50', '#F44336']
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, 
               wedgeprops={'edgecolor': 'white', 'linewidth': 1}, shadow=True)
        ax.axis('equal')
        ax.set_title('Attendance Distribution', fontsize=16)
        
        return fig
    except Exception as e:
        logger.error(f"Error creating pie chart: {str(e)}")
        st.error("Error creating visualization. Please try again.")
        return None

def main():
    st.title("📚 College Attendance Analyzer")
    st.write("Upload your attendance PDF to analyze attendance and plan future classes")
    
    # App version in sidebar
    st.sidebar.markdown(f"**App Version:** {APP_VERSION}")
    
    # Add more info about the app
    with st.sidebar.expander("About the App"):
        st.markdown("""
        This app helps students analyze their attendance reports and plan their
        attendance strategy to meet college requirements.
        
        **Features:**
        - PDF data extraction
        - Attendance visualization
        - Plan how many classes you need to attend
        - Calculate classes you can safely skip
        - Export results to Excel
        
        **Supported Formats:**
        The app works best with standard college ERP generated PDFs.
        """)
    
    # Add sample PDF download option
    with st.sidebar.expander("Sample PDF"):
        st.write("Don't have a PDF? Download a sample to try out the app.")
        # Sample file would be provided here when available
        st.info("Example PDFs will be available in the next update.")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload attendance PDF", type=["pdf"])
    
    if uploaded_file is not None:
        # Process PDF with error handling
        with st.spinner("Analyzing attendance data..."):
            try:
                attendance_data = cached_extract_attendance_data(uploaded_file)
                
                if not attendance_data or not attendance_data.get('subjects'):
                    st.error("Could not extract attendance data from the PDF. Please check the file format and try again.")
                    return
                    
                # Display success message with student name
                student_name = attendance_data['student_name']
                if student_name != "Unknown":
                    st.success(f"Attendance data extracted for {student_name}")
                else:
                    st.warning("Student name could not be detected. Data extraction may be incomplete.")
                
                # Add tabs for better organization
                tab1, tab2, tab3 = st.tabs(["Current Status", "Planning", "Visualizations"])
                
                with tab1:
                    # Display overall attendance with a pie chart
                    st.subheader("Overall Attendance")
                    overall = attendance_data["overall"]
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Metrics
                        st.metric("Present", overall["Present"])
                        st.metric("Total", overall["Total"])
                        st.metric("Percentage", f"{overall['Percentage']}%", 
                                 delta=f"{overall['Percentage'] - 75:.1f}%" if overall['Percentage'] != 75 else None,
                                 delta_color="normal" if overall['Percentage'] >= 75 else "inverse")
                    
                    with col2:
                        # Pie chart
                        pie_chart = create_pie_chart(overall["Present"], overall["Total"])
                        if pie_chart:
                            st.pyplot(pie_chart)
                    
                    # Display subject-wise attendance
                    st.subheader("Subject-wise Attendance")
                    
                    # If no subjects were found, show a warning
                    if not attendance_data["subjects"]:
                        st.warning("No subject data could be extracted from the PDF. The format may not be supported.")
                        return
                        
                    df = pd.DataFrame(attendance_data["subjects"])
                    
                    # Add a status column
                    df['Status'] = df['Percentage'].apply(lambda x: 
                        "✅ Good" if x >= 75 else 
                        "⚠️ Warning" if x >= 60 else 
                        "❌ Critical")
                    
                    # Display as dataframe with formatting
                    st.dataframe(
                        df.style.apply(lambda row: [
                            'background-color: rgba(76, 175, 80, 0.2)' if row['Percentage'] >= 75 else
                            'background-color: rgba(255, 193, 7, 0.2)' if row['Percentage'] >= 60 else
                            'background-color: rgba(244, 67, 54, 0.2)'
                            for _ in row
                        ], axis=1),
                        use_container_width=True
                    )
                    
                    # Sort subjects by attendance percentage (ascending)
                    sorted_df = df.sort_values(by='Percentage')
                    
                    # Critical subjects alert
                    critical_subjects = sorted_df[sorted_df['Percentage'] < 60]
                    if not critical_subjects.empty:
                        st.error(f"⚠️ You have {len(critical_subjects)} subjects with critical attendance (below 60%)")
                        st.dataframe(
                            critical_subjects[['Subject', 'Type', 'Present', 'Total', 'Percentage']],
                            use_container_width=True
                        )
                    
                    # Show heatmap visualization
                    st.subheader("Attendance Heatmap")
                    heatmap = create_attendance_heatmap(df)
                    if heatmap:
                        st.pyplot(heatmap)
                
                with tab2:
                    st.subheader("Attendance Planning")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("### Classes Needed to Reach Target")
                        target_percentage = st.slider("Target Attendance Percentage", 
                                                     min_value=75.0, 
                                                     max_value=100.0, 
                                                     value=75.0, 
                                                     step=0.5, 
                                                     key="target_slider")
                        
                        # Add analysis for overall and each subject
                        classes_needed = {}
                        try:
                            classes_needed["Overall"] = calculate_classes_needed(
                                overall["Present"], 
                                overall["Total"], 
                                target_percentage
                            )
                            
                            for subject in attendance_data["subjects"]:
                                classes_needed[f"{subject['Subject']} ({subject['Type']})"] = calculate_classes_needed(
                                    subject["Present"], 
                                    subject["Total"], 
                                    target_percentage
                                )
                        except Exception as e:
                            logger.error(f"Error calculating classes needed: {str(e)}")
                            st.error("Error in attendance calculations. Please try again.")
                            classes_needed = {"Overall": 0}
                        
                        # Handle infinity values for display
                        needed_df = pd.DataFrame({
                            "Subject": list(classes_needed.keys()),
                            "Current %": [overall["Percentage"]] + [s["Percentage"] for s in attendance_data["subjects"]],
                            "Classes Needed": ["Impossible" if isinstance(v, float) and v == float('inf') else v for v in classes_needed.values()]
                        })
                        
                        # Apply formatting
                        st.dataframe(
                            needed_df,
                            use_container_width=True
                        )
                        
                        # Show special note for impossible cases
                        if any(isinstance(v, float) and v == float('inf') for v in classes_needed.values()):
                            st.info("⚠️ 'Impossible' means you can't reach the target percentage even by attending all remaining classes. Consider speaking with your professor.")
                    
                    with col2:
                        st.write("### Classes You Can Skip")
                        maintain_percentage = st.slider("Maintain Attendance Above", 
                                                       min_value=75.0, 
                                                       max_value=100.0, 
                                                       value=75.0, 
                                                       step=0.5,
                                                       key="maintain_slider")
                        
                        upcoming_classes = st.number_input("Upcoming Classes", 
                                                          min_value=1, 
                                                          max_value=50, 
                                                          value=10,
                                                          step=1)
                        
                        # Calculate classes that can be skipped
                        skippable = {}
                        try:
                            skippable["Overall"] = calculate_classes_can_miss(
                                overall["Present"], 
                                overall["Total"], 
                                maintain_percentage, 
                                upcoming_classes
                            )
                            
                            for subject in attendance_data["subjects"]:
                                skippable[f"{subject['Subject']} ({subject['Type']})"] = calculate_classes_can_miss(
                                    subject["Present"], 
                                    subject["Total"], 
                                    maintain_percentage, 
                                    upcoming_classes
                                )
                        except Exception as e:
                            logger.error(f"Error calculating skippable classes: {str(e)}")
                            st.error("Error in calculations. Please try again.")
                            skippable = {"Overall": 0}
                        
                        # Display as dataframe
                        skip_df = pd.DataFrame({
                            "Subject": list(skippable.keys()),
                            "Current %": [overall["Percentage"]] + [s["Percentage"] for s in attendance_data["subjects"]],
                            "Classes You Can Skip": list(skippable.values())
                        })
                        
                        # Apply formatting
                        st.dataframe(
                            skip_df.style.apply(lambda row: [
                                'background-color: rgba(76, 175, 80, 0.2)' if row['Classes You Can Skip'] > 0 else
                                'background-color: rgba(244, 67, 54, 0.2)'
                                for _ in row
                            ], axis=1),
                            use_container_width=True
                        )
                    
                    # Attendance trend prediction
                    st.subheader("Attendance Trend Prediction")
                    st.write("This chart shows how your attendance will change over the next few classes depending on whether you attend or miss them.")
                    
                    future_classes = st.slider("Number of Future Classes to Predict", 
                                              min_value=5, 
                                              max_value=30, 
                                              value=15, 
                                              step=1)
                    
                    trend_chart = create_attendance_trend_prediction(
                        overall["Present"], 
                        overall["Total"], 
                        target=target_percentage,
                        future_classes=future_classes
                    )
                    
                    if trend_chart:
                        st.altair_chart(trend_chart, use_container_width=True)
                
                with tab3:
                    st.subheader("Advanced Visualizations")
                    
                    if not attendance_data["subjects"]:
                        st.warning("No subject data available for visualization.")
                        return
                    
                    # Bar chart comparing current vs required
                    st.write("### Current vs Required Attendance")
                    
                    chart_data = pd.DataFrame({
                        "Subject": [s["Subject"] + f" ({s['Type']})" for s in attendance_data["subjects"]],
                        "Current": [s["Percentage"] for s in attendance_data["subjects"]],
                        "Required": [target_percentage] * len(attendance_data["subjects"])
                    })
                    
                    try:
                        bar_chart = alt.Chart(chart_