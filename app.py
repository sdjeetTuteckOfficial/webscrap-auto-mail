import streamlit as st
import pandas as pd
from scraper import scrape_job_posting
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
    job_desc, job_email = scrape_job_posting(job_url)
    st.write("Job Description:", job_desc[:500] + "...")
    
    matches = query_roles(job_desc)
    st.write("Matched Roles:")
    for i, (role, url) in enumerate(zip(matches['metadatas'][0], matches['documents'][0])):
        st.write(f"Role: {role['role']}, Portfolio URL: {role['url']}")

    # Generate email body - simple template here
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

    if job_email and st.button("Send Email"):
        from_email = st.text_input("Your Email")
        password = st.text_input("Email Password or App Password", type="password")
        send_email(job_email, f"Opportunity for {matched_role}", email_body, from_email, password)
        st.success("Email sent!")
