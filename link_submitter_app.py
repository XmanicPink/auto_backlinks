
# Streamlit App: External Link Submitter (Secure Version)
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd

st.set_page_config(page_title="🔗 Link Submitter", layout="centered")
st.title("🔗 External Link Submitter")
st.markdown("This tool reads your Google Sheet and submits your site to a list of directories.")

sheet_id = st.text_input("Enter your Google Sheet ID (from the URL)")

if sheet_id:
    run = st.button("🚀 Start Submission")

    if run:
        with st.spinner("Connecting to Google Sheets and starting automation..."):
            try:
                # Use secrets from .streamlit/secrets.toml
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]

                creds = Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"], scopes=scope
                )
                client = gspread.authorize(creds)
                sheet = client.open_by_key(sheet_id).sheet1
                rows = sheet.get_all_records()

                # Setup headless browser
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                driver = webdriver.Chrome(options=chrome_options)

                report = []

                for row in rows:
                    url = row['Target URL']
                    try:
                        driver.get(url)
                        time.sleep(5)
                        driver.find_element(By.NAME, "business_name").send_keys(row['Business Name'])
                        driver.find_element(By.NAME, "website").send_keys(row['Website'])
                        driver.find_element(By.NAME, "phone").send_keys(row['Phone'])
                        driver.find_element(By.NAME, "address").send_keys(row['Address'])
                        driver.find_element(By.NAME, "description").send_keys(row['Description'])
                        driver.find_element(By.NAME, "submit").click()
                        status = "✅ Success"
                    except Exception as e:
                        status = f"❌ Failed: {str(e)[:60]}"
                    report.append({"Site": url, "Status": status})
                    time.sleep(int(row['Delay in Seconds']))

                driver.quit()
                st.success("✅ All done! Here's the report:")
                st.dataframe(pd.DataFrame(report))

            except Exception as err:
                st.error(f"Something went wrong: {err}")
