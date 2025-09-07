import streamlit as st
import pandas as pd
import subprocess
import os

st.set_page_config(page_title="Wealth Manager Executive Summary", layout="wide")

st.title("Wealth Manager Executive Summary")

# Path to your dataset (update as needed)
data_path = st.sidebar.text_input("CSV file path", "synthetic_training_data.csv")

# Load dataset and extract user IDs and names
def get_user_options(csv_path):
    try:
        df = pd.read_csv(csv_path)
        df.columns = [c.strip() for c in df.columns]
        if 'profile__user_id' in df.columns and 'profile__name' in df.columns:
            users = df[['profile__user_id', 'profile__name']].drop_duplicates()
            options = users.apply(lambda row: f"{row['profile__user_id']} - {row['profile__name']}", axis=1).tolist()
            return options, users
        else:
            return [], pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return [], pd.DataFrame()

user_options, users_df = get_user_options(data_path)

selected_user = st.sidebar.selectbox("Select User", user_options)
run_analysis = st.sidebar.button("Run Analysis")

if selected_user and run_analysis:
    user_id = selected_user.split(" - ")[0]
    st.info(f"Selected User: {selected_user}")
    # Build and run the command in the terminal
    output_dir = "./output_streamlit"
    os.makedirs(output_dir, exist_ok=True)
    cmd = f"python src/app/multi_agent_wealth_manager.py --input {data_path} --output {output_dir} --user_id {user_id}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        st.error(f"Error running pipeline: {result.stderr}")
    else:
        st.success("Analysis complete!")
        # Read and display executive summary
        report_path = os.path.join(output_dir, "wealth_report.md")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                summary = f.read()
            st.markdown(summary)
        else:
            st.warning("No executive summary found for this user.")
else:
    st.info("Select a user and click 'Run Analysis' to view their executive summary.")
