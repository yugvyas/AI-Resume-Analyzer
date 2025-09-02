# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import numpy as np

# def show_enhanced_analytics():
#     """Enhanced analytics page with comprehensive visualizations."""
    
#     st.markdown("""
#     <h1 style="text-align: center; color: #1f77b4; margin-bottom: 2rem;">
#         📊 Resume Analytics Dashboard
#     </h1>
#     """, unsafe_allow_html=True)
    
#     if "extracted_data" not in st.session_state or not st.session_state.extracted_data:
#         st.error("No analysis data available. Please analyze a resume first.")
#         if st.button("← Back to Upload"):
#             st.session_state.page = "main"
#             st.rerun()
#         return
    
#     data = st.session_state.extracted_data
    
#     # Main metrics row
#     col1, col2, col3, col4 = st.columns(4)
    
#     overall_score = data.get("overall_score", 0)
#     matching_skills = len(data.get("keyword_matching", []))
#     missing_skills = len(data.get("missing_keywords", []))
#     suggestions_count = len(data.get("suggestions", []))
    
#     with col1:
#         st.metric(
#             label="Overall Match Score",
#             value=f"{overall_score}%",
#             delta=f"{overall_score - 70}%" if overall_score != 70 else None
#         )
    
#     with col2:
#         st.metric(
#             label="Matched Skills",
#             value=matching_skills,
#             delta="Good" if matching_skills > 5 else "Needs Work"
#         )
    
#     with col3:
#         st.metric(
#             label="Missing Skills", 
#             value=missing_skills,
#             delta="Too Many" if missing_skills > 5 else "Manageable"
#         )
    
#     with col4:
#         ats_score = data.get("ats_score", data.get("ats_breakdown", {}).get("overall_ats_score", 50))
#         st.metric(
#             label="ATS Compatible",
#             value=f"{ats_score:.0f}%",
#             delta="Good" if ats_score > 75 else "Needs Work"
#         )
    
#     # Score visualization
#     st.subheader("📈 Detailed Score Analysis")
    
#     col1, col2 = st.columns([1, 1])
    
#     with col1:
#         # Gauge chart for overall score
#         fig = go.Figure(go.Indicator(
#             mode="gauge+number",
#             value=overall_score,
#             domain={'x': [0, 1], 'y': [0, 1]},
#             title={'text': "Resume Match Score"},
#             gauge={
#                 'axis': {'range': [None, 100]},
#                 'bar': {'color': "darkblue"},
#                 'steps': [
#                     {'range': [0, 50], 'color': "lightgray"},
#                     {'range': [50, 80], 'color': "yellow"},
#                     {'range': [80, 100], 'color': "lightgreen"}
#                 ],
#                 'threshold': {
#                     'line': {'color': "red", 'width': 4},
#                     'thickness': 0.75,
#                     'value': 90
#                 }
#             }
#         ))
#         fig.update_layout(height=300)
#         st.plotly_chart(fig, use_container_width=True)
    
#     with col2:
#         # ATS breakdown chart
#         ats_data = data.get("ats_breakdown", {})
#         if ats_data:
#             ats_df = pd.DataFrame([
#                 {"Factor": "Keyword Density", "Score": ats_data.get("keyword_density", 50)},
#                 {"Factor": "Section Structure", "Score": ats_data.get("section_structure", 50)},
#                 {"Factor": "Formatting", "Score": ats_data.get("formatting", 50)}
#             ])
            
#             fig = px.bar(ats_df, x='Factor', y='Score', 
#                         title="ATS Compatibility Breakdown",
#                         color='Score', 
#                         color_continuous_scale='RdYlGn')
#             fig.update_layout(height=300)
#             st.plotly_chart(fig, use_container_width=True)
    
#     # Skills analysis
#     st.subheader("🎯 Skills Analysis")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("#### ✅ Matched Skills")
#         matched = data.get("keyword_matching", [])
#         if matched:
#             for skill in matched[:8]:  # Show top 8
#                 st.success(f"✓ {skill}")
            
#             if len(matched) > 8:
#                 with st.expander(f"View all {len(matched)} matched skills"):
#                     for skill in matched[8:]:
#                         st.write(f"✓ {skill}")
#         else:
#             st.warning("No matching skills found")
    
#     with col2:
#         st.markdown("#### ❌ Missing Skills")
#         missing = data.get("missing_keywords", [])
#         if missing:
#             for skill in missing[:8]:  # Show top 8
#                 st.error(f"✗ {skill}")
            
#             if len(missing) > 8:
#                 with st.expander(f"View all {len(missing)} missing skills"):
#                     for skill in missing[8:]:
#                         st.write(f"✗ {skill}")
#         else:
#             st.success("No critical missing skills!")
    
#     # Skills comparison visualization
#     if matched or missing:
#         st.subheader("📊 Skills Overview")
        
#         skills_data = pd.DataFrame({
#             'Category': ['Matched Skills', 'Missing Skills'],
#             'Count': [len(matched), len(missing)]
#         })
        
#         fig = px.pie(skills_data, values='Count', names='Category',
#                      color_discrete_map={
#                          'Matched Skills': '#2ECC71',
#                          'Missing Skills': '#E74C3C'
#                      })
#         fig.update_layout(height=400)
#         st.plotly_chart(fig, use_container_width=True)
    
#     # Improvement suggestions
#     st.subheader("🚀 Improvement Suggestions")
    
#     suggestions = data.get("suggestions", [])
#     if suggestions:
#         # Categorize suggestions by priority
#         for i, suggestion in enumerate(suggestions, 1):
#             priority = "🔴 High" if any(word in suggestion.lower() for word in ['skill', 'experience', 'certification']) else "🟡 Medium"
            
#             with st.container():
#                 st.markdown(f"**{priority} Priority {i}:**")
#                 st.write(suggestion)
#                 st.markdown("---")
    
#     # Action buttons
#     st.subheader("📥 Next Steps")
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         if st.button("📄 Download Report", use_container_width=True):
#             report_content = f"""
# RESUME ANALYSIS REPORT
# =====================

# Overall Score: {overall_score}%
# ATS Compatibility: {data.get('ats_score', 50):.0f}%

# MATCHED SKILLS ({len(matched)}):
# {chr(10).join(f"• {skill}" for skill in matched)}

# MISSING SKILLS ({len(missing)}):
# {chr(10).join(f"• {skill}" for skill in missing)}

# IMPROVEMENT SUGGESTIONS:
# {chr(10).join(f"{i}. {suggestion}" for i, suggestion in enumerate(suggestions, 1))}

# Generated by AI Resume Matcher
# Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
#             """
            
#             st.download_button(
#                 label="Download as TXT",
#                 data=report_content,
#                 file_name=f"resume_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
#                 mime="text/plain"
#             )
    
#     with col2:
#         if st.button("🔄 Analyze Another", use_container_width=True):
#             # Clear session state
#             for key in ['extracted_data', 'resume_uploaded', 'uploaded_file', 'analysis_complete']:
#                 if key in st.session_state:
#                     del st.session_state[key]
#             st.session_state.page = "main"
#             st.rerun()
    
#     with col3:
#         if st.button("📧 Share Results", use_container_width=True):
#             st.info("Feature coming soon: Email results!")

#     # Add this to the bottom of your app.py
#         # Update the analytics page call
#         elif st.session_state.page == "analytics":
#             from enhanced_analytics import show_enhanced_analytics
#             show_enhanced_analytics()












import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def show_enhanced_analytics():
    """Enhanced analytics page with comprehensive visualizations."""
    
    st.markdown("""
    <h1 style="text-align: center; color: #1f77b4; margin-bottom: 2rem;">
        📊 Resume Analytics Dashboard
    </h1>
    """, unsafe_allow_html=True)
    
    if "extracted_data" not in st.session_state or not st.session_state.extracted_data:
        st.error("No analysis data available. Please analyze a resume first.")
        if st.button("← Back to Upload"):
            st.session_state.page = "main"
            st.rerun()
        return
    
    data = st.session_state.extracted_data
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    overall_score = data.get("overall_score", 0)
    matching_skills = len(data.get("keyword_matching", []))
    missing_skills = len(data.get("missing_keywords", []))
    suggestions_count = len(data.get("suggestions", []))
    
    with col1:
        st.metric(
            label="Overall Match Score",
            value=f"{overall_score}%",
            delta=f"{overall_score - 70}%" if overall_score != 70 else None
        )
    
    with col2:
        st.metric(
            label="Matched Skills",
            value=matching_skills,
            delta="Good" if matching_skills > 5 else "Needs Work"
        )
    
    with col3:
        st.metric(
            label="Missing Skills", 
            value=missing_skills,
            delta="Too Many" if missing_skills > 5 else "Manageable"
        )
    
    with col4:
        ats_score = data.get("ats_score", data.get("ats_breakdown", {}).get("overall_ats_score", 50))
        st.metric(
            label="ATS Compatible",
            value=f"{ats_score:.0f}%",
            delta="Good" if ats_score > 75 else "Needs Work"
        )
    
    # Score visualization
    st.subheader("📈 Detailed Score Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Gauge chart for overall score
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Resume Match Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ATS breakdown chart
        ats_data = data.get("ats_breakdown", {})
        if ats_data:
            ats_df = pd.DataFrame([
                {"Factor": "Keyword Density", "Score": ats_data.get("keyword_density", 50)},
                {"Factor": "Section Structure", "Score": ats_data.get("section_structure", 50)},
                {"Factor": "Formatting", "Score": ats_data.get("formatting", 50)}
            ])
            
            fig = px.bar(ats_df, x='Factor', y='Score', 
                        title="ATS Compatibility Breakdown",
                        color='Score', 
                        color_continuous_scale='RdYlGn')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # Skills analysis
    st.subheader("🎯 Skills Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Matched Skills")
        matched = data.get("keyword_matching", [])
        if matched:
            for skill in matched[:8]:  # Show top 8
                st.success(f"✓ {skill}")
            
            if len(matched) > 8:
                with st.expander(f"View all {len(matched)} matched skills"):
                    for skill in matched[8:]:
                        st.write(f"✓ {skill}")
        else:
            st.warning("No matching skills found")
    
    with col2:
        st.markdown("#### ❌ Missing Skills")
        missing = data.get("missing_keywords", [])
        if missing:
            for skill in missing[:8]:  # Show top 8
                st.error(f"✗ {skill}")
            
            if len(missing) > 8:
                with st.expander(f"View all {len(missing)} missing skills"):
                    for skill in missing[8:]:
                        st.write(f"✗ {skill}")
        else:
            st.success("No critical missing skills!")
    
    # Skills comparison visualization
    if matched or missing:
        st.subheader("📊 Skills Overview")
        
        skills_data = pd.DataFrame({
            'Category': ['Matched Skills', 'Missing Skills'],
            'Count': [len(matched), len(missing)]
        })
        
        fig = px.pie(skills_data, values='Count', names='Category',
                     color_discrete_map={
                         'Matched Skills': '#2ECC71',
                         'Missing Skills': '#E74C3C'
                     })
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Improvement suggestions
    st.subheader("🚀 Improvement Suggestions")
    
    suggestions = data.get("suggestions", [])
    if suggestions:
        # Categorize suggestions by priority
        for i, suggestion in enumerate(suggestions, 1):
            priority = "🔴 High" if any(word in suggestion.lower() for word in ['skill', 'experience', 'certification']) else "🟡 Medium"
            
            with st.container():
                st.markdown(f"**{priority} Priority {i}:**")
                st.write(suggestion)
                st.markdown("---")
    
    # Action buttons
    st.subheader("📥 Next Steps")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download Report", use_container_width=True):
            report_content = f"""
RESUME ANALYSIS REPORT
=====================

Overall Score: {overall_score}%
ATS Compatibility: {data.get('ats_score', 50):.0f}%

MATCHED SKILLS ({len(matched)}):
{chr(10).join(f"• {skill}" for skill in matched)}

MISSING SKILLS ({len(missing)}):
{chr(10).join(f"• {skill}" for skill in missing)}

IMPROVEMENT SUGGESTIONS:
{chr(10).join(f"{i}. {suggestion}" for i, suggestion in enumerate(suggestions, 1))}

Generated by AI Resume Matcher
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
            """
            
            st.download_button(
                label="Download as TXT",
                data=report_content,
                file_name=f"resume_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("🔄 Analyze Another", use_container_width=True):
            # Clear session state
            for key in ['extracted_data', 'resume_uploaded', 'uploaded_file', 'analysis_complete']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = "main"
            st.rerun()
    
    with col3:
        if st.button("📧 Share Results", use_container_width=True):
            st.info("Feature coming soon: Email results!")