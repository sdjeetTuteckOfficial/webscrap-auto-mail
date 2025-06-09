import streamlit as st
import pandas as pd
from scraper import scrape_job_postings
from embed import add_roles_from_excel, query_roles
from emailer import send_email

st.title("Cold Email Generator for BDE")

uploaded_file = st.file_uploader("Upload Roles Excel", type=["xlsx"])
if uploaded_file:
    df_roles = pd.read_excel(uploaded_file)
    add_roles_from_excel(df_roles)
    st.success("Roles loaded and indexed.")

job_url = st.text_input("Enter Job Posting URL")

if st.button("Scrape and Match"):
    job_postings = scrape_job_postings(job_url)
    if not job_postings:
        st.error("No job postings found or failed to scrape.")
    else:
        # Save job postings in session state
        st.session_state['job_postings'] = job_postings
        st.session_state['selected_index'] = 0  # default selection index

if 'job_postings' in st.session_state:
    job_postings = st.session_state['job_postings']

    options = [f"{job['title']} ({job['email'] or 'No email'})" for job in job_postings]
    selected = st.selectbox("Select a job posting", options, key="job_select")

    selected_index = options.index(selected)
    st.session_state['selected_index'] = selected_index

    selected_job = job_postings[selected_index]
    job_desc = selected_job['description']
    job_email = selected_job['email']

    st.write("Job Description:", job_desc[:500] + "...")

    matches = query_roles(job_desc)
    st.write("Matched Roles:")
    for i, (role, url) in enumerate(zip(matches['metadatas'][0], matches['documents'][0])):
        st.write(f"Role: {role['role']}, Portfolio URL: {role['url']}")

    matched_role = matches['metadatas'][0][0]['role']
    portfolio_url = matches['metadatas'][0][0]['url']

    email_body = f"""
Hi,

I saw your job posting for {matched_role} and thought you might be interested in our services.
You can check our portfolio here: {portfolio_url}

Looking forward to connecting!

Best regards,
NorthLab
"""
    st.code(email_body)

    if job_email:
        from_email = st.text_input("Your Email")
        password = st.text_input("Email Password or App Password", type="password")
        if st.button("Send Email"):
            if from_email and password:
                send_email(job_email, f"Opportunity for {matched_role}", email_body, from_email, password)
                st.success("Email sent!")
            else:
                st.error("Please enter your email and password to send.")
    else:
        st.warning("No email found for this job posting, cannot send email.")
