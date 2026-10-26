import datetime
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Exam Consistency & Tracker", page_icon="🎯", layout="wide"
)

# Custom Styling for Warning Banners
st.markdown(
    """
    <style>
    .warning-box {
        padding: 15px;
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .success-box {
        padding: 10px;
        background-color: #2e7d32;
        color: white;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎯 Multi-Exam Consistency & Study Command Center")
st.write(
    "Track daily progress, exam-specific syllabus completion, test performance, and screen time."
)

# --- EXAM SYLLABUS DICTIONARIES ---
exam_syllabi = {
    "UPSC Civil Services": {
        "Geography Optional": [
            "Geomorphology",
            "Climatology",
            "Oceanography",
            "Biogeography",
            "Perspective in Human Geography",
            "Economic Geography",
            "Population & Settlement",
            "Regional Planning",
            "Models & Theories in Geography",
        ],
        "General Studies - 1": [
            "Indian Heritage & Culture",
            "Modern Indian History",
            "World History",
            "Indian Society",
            "Physical & World Geography",
        ],
        "General Studies - 2": [
            "Indian Constitution & Polity",
            "Governance & Social Justice",
            "Social Sector & Welfare",
            "International Relations",
        ],
        "General Studies - 3": [
            "Indian Economy & Resources",
            "Agriculture & Food Security",
            "Science & Technology",
            "Environment & Biodiversity",
            "Disaster Management",
            "Internal Security",
        ],
        "General Studies - 4": [
            "Ethics and Human Interface",
            "Attitude & Aptitude",
            "Emotional Intelligence",
            "Contributions of Moral Thinkers",
            "Probity in Governance & Case Studies",
        ],
    },
    "CAT": {
        "Quantitative Aptitude": [
            "Arithmetic (Percentages, Profit & Loss, Ratio)",
            "Algebra (Equations, Inequalities, Functions)",
            "Geometry & Mensuration",
            "Number Systems",
            "Modern Math (Permutations, Probability)",
        ],
        "Data Interpretation & Logical Reasoning (DILR)": [
            "Data Tables & Charts",
            "Venn Diagrams & Sets",
            "Games & Tournaments",
            "Routes & Networks",
            "Logical Reasoning Puzzles",
        ],
        "Verbal Ability & Reading Comprehension (VARC)": [
            "Reading Comprehension Practice",
            "Para Jumbles & Summary",
            "Paragraph Completion",
            "Critical Reasoning",
        ],
    },
    "GATE": {
        "Engineering Mathematics": [
            "Linear Algebra",
            "Calculus",
            "Differential Equations",
            "Probability & Statistics",
            "Numerical Methods",
        ],
        "Core Technical Subjects": [
            "Data Structures & Algorithms",
            "Database Management Systems (DBMS)",
            "Operating Systems",
            "Computer Networks",
            "Digital Logic & Computer Architecture",
        ],
        "General Aptitude": [
            "Verbal Aptitude",
            "Numerical Aptitude",
            "Spatial Aptitude",
        ],
    },
    "APPSC / TGPSC Groups": {
        "General Studies & Mental Ability": [
            "Current Affairs (Regional, National, International)",
            "General Science & Tech",
            "Environmental Issues & Disaster Management",
            "Indian Geography & Polity",
            "Logical Reasoning & Analytical Ability",
        ],
        "State Specific History & Culture": [
            "History of Movement for Telangana / Andhra Pradesh",
            "State Economy, Policies & Schemes",
            "Society, Culture, Heritage, Arts & Literature",
            "Geography of the State",
        ],
    },
    "SSC CGL": {
        "Quantitative Aptitude": [
            "Computation of Whole Numbers, Decimals, Fractions",
            "Percentage, Ratio & Proportion, Square Roots",
            "Interest, Profit & Loss, Discount, Partnership",
            "Algebra & Basic Identities",
            "Geometry, Mensuration, Trigonometry",
        ],
        "Reasoning & General Intelligence": [
            "Analogies, Similarities & Differences",
            "Space Visualization, Spatial Orientation",
            "Problem Solving, Analysis, Judgment",
            "Coding-Decoding & Series",
        ],
        "English Comprehension": [
            "Vocabulary & Synonyms/Antonyms",
            "Grammar & Sentence Correction",
            "Reading Comprehension",
            "Active/Passive Voice & Direct/Indirect Speech",
        ],
        "General Awareness": [
            "Indian History, Culture & Polity",
            "Geography & Economy",
            "General Science & Current Affairs",
        ],
    },
}

# --- INITIALIZE SESSION STATE ---
if "target_exam" not in st.session_state:
    st.session_state.target_exam = "UPSC Civil Services"

if "logs" not in st.session_state:
    st.session_state.logs = pd.DataFrame(
        columns=[
            "Date",
            "Exam",
            "Subject",
            "Hours",
            "Tests_Done",
            "Screen_Time_Mins",
            "Consistency_Marked",
        ]
    )

if "completed_topics" not in st.session_state:
    # Stored as a dictionary mapping exam -> set of completed topics
    st.session_state.completed_topics = {exam: set() for exam in exam_syllabi}

# --- SIDEBAR: EXAM SELECTOR, SCREEN TIME & LOGGING ---
st.sidebar.header("🎯 Target & Screen Time")

# Exam Selection dropdown at the very top of sidebar
selected_exam = st.sidebar.selectbox(
    "Select Target Exam",
    list(exam_syllabi.keys()),
    index=list(exam_syllabi.keys()).index(st.session_state.target_exam),
)
st.session_state.target_exam = selected_exam

st.sidebar.markdown("---")
log_date = st.sidebar.date_input("Date", datetime.date.today())

# Dynamically populate subjects based on selected exam
available_subjects = list(exam_syllabi[selected_exam].keys()) + [
    "General Practice / Mock Tests",
    "Current Affairs / Revision",
]
subject_selected = st.sidebar.selectbox("Focus Subject", available_subjects)

study_hours = st.sidebar.number_input(
    "Study Hours", min_value=0.0, max_value=16.0, step=0.5, value=2.0
)
tests_count = st.sidebar.number_input(
    "Tests / Answers Written", min_value=0, max_value=10, step=1, value=0
)
screen_time = st.sidebar.number_input(
    "Today's Screen Time (Minutes)",
    min_value=0,
    max_value=1440,
    step=5,
    value=45,
)
consistency_checked = st.sidebar.checkbox("Mark Day as Consistent ✅", value=True)

# Screen-Time Logic Check
if screen_time > 60:
    st.markdown(
        f'<div class="warning-box">⚠️ WARNING: Screen time has crossed 1 hour ({screen_time} mins)! Refocus on your targets!</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="success-box">✅ Screen time is within control limit ({screen_time} mins). Keep it up!</div>',
        unsafe_allow_html=True,
    )

if st.sidebar.button("Save Daily Log"):
    new_entry = pd.DataFrame(
        [
            {
                "Date": str(log_date),
                "Exam": selected_exam,
                "Subject": subject_selected,
                "Hours": study_hours,
                "Tests_Done": tests_count,
                "Screen_Time_Mins": screen_time,
                "Consistency_Marked": consistency_checked,
            }
        ]
    )
    st.session_state.logs = pd.concat(
        [st.session_state.logs, new_entry], ignore_index=True
    )
    st.sidebar.success("Log saved successfully!")

# --- MAIN APP TABS ---
tab1, tab2, tab3 = st.tabs(
    [
        "📊 Consistency & Analytics",
        f"📚 {selected_exam} Syllabus Tracker",
        "📝 Test Logs History",
    ]
)

with tab1:
    st.subheader(f"Analytics for: {selected_exam}")

    if not st.session_state.logs.empty:
        df = st.session_state.logs
        # Filter logs for current exam if desired, or show overall. Let's filter by selected exam for precision:
        exam_df = df[df["Exam"] == selected_exam]

        # Metrics overview
        total_hours = exam_df["Hours"].sum() if not exam_df.empty else 0
        total_tests = exam_df["Tests_Done"].sum() if not exam_df.empty else 0
        consistent_days = (
            exam_df[exam_df["Consistency_Marked"] == True]["Date"].nunique()
            if not exam_df.empty
            else 0
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Study Hours", f"{total_hours} hrs")
        col2.metric("Tests / Mocks Logged", total_tests)
        col3.metric("Consistent Days Active", consistent_days)

        st.markdown("---")
        st.write(f"### Hours Studied per Subject ({selected_exam})")
        if not exam_df.empty:
            subject_grouped = exam_df.groupby("Subject")["Hours"].sum().reset_index()
            st.bar_chart(subject_grouped.set_index("Subject"))
        else:
            st.info(f"No logs recorded yet for {selected_exam}.")

        st.write("### Complete Log History Across All Exams")
        st.dataframe(df, use_container_width=True)
    else:
        st.info(
            "No logs recorded yet. Use the sidebar input fields to submit your first study session!"
        )

with tab2:
    st.subheader(f"📖 {selected_exam} Syllabus & Module Tracker")
    st.write(
        "Check off modules as you complete reading, revision, and practice tests."
    )

    current_syllabus = exam_syllabi[selected_exam]
    completed_set = st.session_state.completed_topics[selected_exam]

    for subject, topics in current_syllabus.items():
        with st.expander(f"📁 {subject}"):
            for topic in topics:
                is_checked = topic in completed_set
                if st.checkbox(topic, value=is_checked, key=f"{selected_exam}_{topic}"):
                    completed_set.add(topic)
                else:
                    if topic in completed_set:
                        completed_set.remove(topic)

    # Progress Calculation
    all_topics_flat = [t for sublist in current_syllabus.values() for t in sublist]
    completed_count = len(completed_set)
    total_topics_count = len(all_topics_flat)
    progress_pct = (
        int((completed_count / total_topics_count) * 100)
        if total_topics_count > 0
        else 0
    )

    st.markdown("---")
    st.write(
        f"**{selected_exam} Syllabus Progress:** {completed_count}/{total_topics_count} Topics ({progress_pct}%)"
    )
    st.progress(progress_pct)

with tab3:
    st.subheader("Test Analytics & Performance Record")
    if not st.session_state.logs.empty:
        test_df = st.session_state.logs[
            st.session_state.logs["Tests_Done"] > 0
        ][["Date", "Exam", "Subject", "Tests_Done", "Screen_Time_Mins"]]
        if not test_df.empty:
            st.dataframe(test_df, use_container_width=True)
        else:
            st.write(
                "No tests or practice papers logged yet. Update test counts via the sidebar."
            )
    else:
        st.write("No data available yet.")