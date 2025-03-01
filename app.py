import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
import altair as alt

# Import utility functions
from utils.pdf_extractor import extract_attendance_data
from utils.attendance_calc import (
    calculate_classes_needed,
    calculate_classes_can_miss
)

# Streamlit UI
st.set_page_config(
    page_title="College Attendance Analyzer",
    page_icon="📊",
    layout="wide"
)

def create_attendance_heatmap(df):
    """Create a heatmap for attendance visualization"""
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
    
    fig, ax = plt.subplots(figsize=(10, len(subjects) * 0.4))
    
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

def create_attendance_trend_prediction(present, total, target=75, future_classes=15):
    """Create a trend chart showing how attendance will change with each class"""
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

def create_pie_chart(present, total):
    """Create a pie chart showing attendance distribution"""
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

st.title("📚 College Attendance Analyzer")
st.write("Upload your attendance PDF to analyze attendance and plan future classes")

# File uploader
uploaded_file = st.file_uploader("Upload attendance PDF", type=["pdf"])

if uploaded_file is not None:
    # Process PDF
    with st.spinner("Analyzing attendance data..."):
        attendance_data = extract_attendance_data(uploaded_file)
    
    st.success(f"Attendance data extracted for {attendance_data['student_name']}")
    
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
            st.pyplot(pie_chart)
        
        # Display subject-wise attendance
        st.subheader("Subject-wise Attendance")
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
        
        # Show heatmap visualization
        st.subheader("Attendance Heatmap")
        heatmap = create_attendance_heatmap(df)
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
            
            # Display as dataframe
            needed_df = pd.DataFrame({
                "Subject": list(classes_needed.keys()),
                "Current %": [overall["Percentage"]] + [s["Percentage"] for s in attendance_data["subjects"]],
                "Classes Needed": list(classes_needed.values())
            })
            
            # Apply formatting
            st.dataframe(
                needed_df.style.apply(lambda row: [
                    'color: green' if row['Classes Needed'] == 0 else 
                    'color: orange' if row['Classes Needed'] <= 5 else 
                    'color: red'
                    for _ in row
                ], axis=1),
                use_container_width=True
            )
        
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
        
        st.altair_chart(trend_chart, use_container_width=True)
    
    with tab3:
        st.subheader("Advanced Visualizations")
        
        # Bar chart comparing current vs required
        st.write("### Current vs Required Attendance")
        
        chart_data = pd.DataFrame({
            "Subject": [s["Subject"] + f" ({s['Type']})" for s in attendance_data["subjects"]],
            "Current": [s["Percentage"] for s in attendance_data["subjects"]],
            "Required": [target_percentage] * len(attendance_data["subjects"])
        })
        
        bar_chart = alt.Chart(chart_data).transform_fold(
            ['Current', 'Required'],
            as_=['Metric', 'Percentage']
        ).mark_bar().encode(
            x=alt.X('Subject:N', sort='-y', title='Subject'),
            y=alt.Y('Percentage:Q', title='Attendance Percentage'),
            color=alt.Color('Metric:N', scale=alt.Scale(domain=['Current', 'Required'], range=['#2196F3', '#757575'])),
            opacity=alt.condition(
                alt.datum.Metric == 'Required',
                alt.value(0.5),
                alt.value(1)
            )
        ).properties(
            title='Current vs Required Attendance',
            width=600,
            height=400
        ).interactive()
        
        st.altair_chart(bar_chart, use_container_width=True)
        
        # Classes to attend visualization
        st.write("### Classes to Attend Visualization")
        
        # Filter out subjects that already meet the requirement
        needed_subjects = {k: v for k, v in classes_needed.items() if v > 0}
        
        if needed_subjects:
            attend_data = pd.DataFrame({
                "Subject": list(needed_subjects.keys()),
                "Classes Needed": list(needed_subjects.values())
            })
            
            attend_chart = alt.Chart(attend_data).mark_bar().encode(
                x=alt.X('Classes Needed:Q', title='Classes Needed to Attend'),
                y=alt.Y('Subject:N', sort='-x', title='Subject'),
                color=alt.Color('Classes Needed:Q', 
                              scale=alt.Scale(scheme='reds'),
                              legend=None)
            ).properties(
                title='Classes Needed to Reach Target Attendance',
                width=600,
                height=min(400, 50 * len(needed_subjects))
            )
            
            # Add text labels
            text = attend_chart.mark_text(
                align='left',
                baseline='middle',
                dx=3
            ).encode(
                text='Classes Needed:Q'
            )
            
            st.altair_chart(attend_chart + text, use_container_width=True)
        else:
            st.success("Congratulations! All subjects already meet or exceed the target attendance.")
    
    # Download processed data
    st.subheader("Download Analysis")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        pd.DataFrame([{"Name": attendance_data["student_name"], 
                      "Overall Attendance": f"{overall['Percentage']}%"}]).to_excel(writer, sheet_name="Summary", index=False)
        df.to_excel(writer, sheet_name="Subjects", index=False)
        needed_df.to_excel(writer, sheet_name="Classes Needed", index=False)
        skip_df.to_excel(writer, sheet_name="Classes Can Skip", index=False)
    
    output.seek(0)
    st.download_button(
        label="Download Analysis as Excel",
        data=output,
        file_name="attendance_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Please upload your attendance PDF to get started")
    
    # Example of what the app does
    st.subheader("What this app does:")
    st.markdown("""
    1. **Extract Attendance Data**: Upload your college ERP attendance PDF
    2. **Analyze Current Status**: See your current attendance percentages for each subject
    3. **Plan Future Attendance**: 
       - Calculate how many more classes you need to attend to reach your target (e.g., 75%)
       - Find out how many classes you can safely skip while maintaining your desired attendance
    4. **Visualize Trends**: See how your attendance will change over future classes
    5. **Download Analysis**: Save the complete analysis as an Excel file
    """)
    
    # Sample image or placeholder
    st.image("https://via.placeholder.com/800x400.png?text=Upload+Your+Attendance+PDF", use_column_width=True)

# Add a footer
st.markdown("---")
st.caption("Attendance Analyzer App | Created with Streamlit and PDF Plumber")