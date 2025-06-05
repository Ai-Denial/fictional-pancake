import streamlit as st
import json
import os
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfMerger

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load denial codes
DENIAL_CODE_FILE = "denial_codes.json"
try:
    with open(DENIAL_CODE_FILE, "r") as f:
        denial_codes = json.load(f)
except Exception as e:
    denial_codes = {}

st.set_page_config(page_title="AI Insurance Appeal Generator", layout="centered")
st.title("📋 AI-Powered Denial Appeal Generator")

if not denial_codes:
    st.warning("Denial codes not found. Please check denial_codes.json file.")
    st.stop()

selected_code = st.selectbox("Select Denial Code", list(denial_codes.keys()))

# Handle fallback for unknown codes
if selected_code not in denial_codes:
    st.info(f"We're adding '{selected_code}' soon! Meanwhile, here's a generic template.")
    info = {
        "description": "This denial code is not in our library yet.",
        "appeal_strategy": "Explain the clinical context and request a re-review.",
        "evidence_tips": "Attach supporting documents like progress notes, labs, or prior auth."
    }
    with open("missing_codes.log", "a") as log:
        log.write(f"{selected_code}\n")
else:
    info = denial_codes[selected_code]

st.subheader(f"{selected_code}: {info.get('description', 'No description')}")
st.markdown(f"**🧠 Appeal Strategy:** {info.get('appeal_strategy', 'N/A')}")
st.markdown(f"**📎 Evidence Tips:** {info.get('evidence_tips', 'N/A')}")

# Optional RARC codes
rarc_options = info.get("rarcs", {})
selected_rarc = None
if rarc_options:
    selected_rarc = st.selectbox("Select Remark Code (RARC)", list(rarc_options.keys()))
    st.markdown(f"**📌 Remark Code Description:** {rarc_options[selected_rarc]}")

# Optional Payer Strategy
payer_options = list(info.get("payers", {}).keys())
selected_payer = st.selectbox("Select Payer (Optional)", payer_options or ["None"])
if selected_payer != "None" and selected_payer in info.get("payers", {}):
    payer_info = info["payers"][selected_payer]
    st.markdown(f"### 🏥 Payer-Specific Strategy for {selected_payer}")
    st.markdown(f"**Modifier Tip:** {payer_info.get('modifier_tip', 'N/A')}")
    st.markdown(f"**Policy Reference:** {payer_info.get('policy_ref', 'N/A')}")
    st.markdown(f"**Notes:** {payer_info.get('extra_notes', '—')}")
else:
    payer_info = {}

st.markdown("---")
st.subheader("✍️ Fill in Appeal Details")

with st.form("appeal_form"):
    full_name = st.text_input("Your Full Name")
    policy_id = st.text_input("Policy/Member ID")
    insurance_company = st.text_input("Insurance Company")
    claim_number = st.text_input("Claim Number")
    denial_date = st.date_input("Denial Date", value=date.today())
    denial_reason = st.text_area("Exact Denial Reason")
    treatment_date = st.date_input("Treatment Date", value=date.today())
    provider_name = st.text_input("Provider Name")
    cpt_codes = st.text_input("CPT Procedure Codes (comma separated)")
    icd10_codes = st.text_input("ICD-10 Diagnosis Codes (comma separated)")
    service_description = st.text_input("Service Description (e.g., MRI of knee)")
    medical_necessity = st.text_area("Medical Necessity (symptoms, test results)")
    policy_basis = st.text_area("Policy Coverage Basis (if known)")
    processing_errors = st.text_area("Processing Errors (if any)")
    submit = st.form_submit_button("Generate Appeal Letter")

if submit:
    if not all([full_name, policy_id, insurance_company, claim_number, denial_date, denial_reason, treatment_date, provider_name]):
        st.warning("Please complete all required fields.")
    else:
        with st.spinner("Generating letter with GPT-4..."):
            try:
                gpt_prompt = f"""
Generate a formal, respectful appeal letter for a health insurance claim denial.

Full Name: {full_name}
Policy/Member ID: {policy_id}
Insurance Company: {insurance_company}
Claim Number: {claim_number}
Denial Date: {denial_date.strftime('%B %d, %Y')}
Treatment Date: {treatment_date.strftime('%B %d, %Y')}
Provider Name: {provider_name}
Denial Code: {selected_code} ({info.get('description', '')})
Denial Reason: {denial_reason}
Appeal Strategy: {info.get('appeal_strategy', '')}
Remark Code: {selected_rarc} - {rarc_options.get(selected_rarc, '') if selected_rarc else 'N/A'}
CPT Codes: {cpt_codes}
ICD-10 Codes: {icd10_codes}
Service Description: {service_description}
Medical Necessity: {medical_necessity}
Policy Coverage Basis: {policy_basis}
Processing Errors: {processing_errors}

Payer-Specific Strategy for {selected_payer}:
Modifier Tip: {payer_info.get('modifier_tip', '')}
Policy Reference: {payer_info.get('policy_ref', '')}
Notes: {payer_info.get('extra_notes', '')}
"""
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": gpt_prompt}],
                    temperature=0.4
                )
                letter = response.choices[0].message.content
                st.success("Letter generated below:")
                st.text_area("Generated Appeal Letter", letter, height=350)
            except Exception as e:
                st.error(f"Error: {e}")

# File upload section
st.markdown("---")
st.subheader("📎 Upload Supporting Documents (EOBs, Clinical Notes, etc.)")

uploaded_files = st.file_uploader(
    "Attach multiple files (PDFs only):", 
    type=["pdf"], 
    accept_multiple_files=True
)

upload_dir = "user_uploads"
os.makedirs(upload_dir, exist_ok=True)

merged_path = os.path.join(upload_dir, "merged_appeal_docs.pdf")

if uploaded_files:
    pdf_files = []
    for file in uploaded_files:
        file_path = os.path.join(upload_dir, file.name)
        with open(file_path, "wb") as f:
            f.write(file.read())
        pdf_files.append(file_path)
        st.markdown(f"- {file.name}")

    # Merge PDFs
    if pdf_files:
        merger = PdfMerger()
        for pdf in pdf_files:
            merger.append(pdf)
        with open(merged_path, "wb") as fout:
            merger.write(fout)
        merger.close()

        st.success("✅ All PDFs merged successfully.")
        with open(merged_path, "rb") as f:
            st.download_button("📥 Download Merged Appeal Packet", f, file_name="merged_appeal_packet.pdf")

# ----------------------------
# 💬 Feedback & Suggest New Codes
# ----------------------------
st.markdown("---")
st.subheader("💬 Feedback & Help Us Improve")

feedback = st.text_area("Can't find your denial code or have suggestions? Let us know:")
eob_file = st.file_uploader("📤 Upload EOB or screenshot (PDF, JPG, PNG) to help us expand our code library:", type=["pdf", "jpg", "jpeg", "png"])

if st.button("Submit Feedback"):
    feedback_logged = False
    eob_uploaded = False

    # Save feedback
    if feedback:
        os.makedirs("feedback_logs", exist_ok=True)
        with open(os.path.join("feedback_logs", "user_feedback.log"), "a") as log_file:
            log_file.write(f"{feedback}\n---\n")
        feedback_logged = True

    # Save EOB upload
    if eob_file:
        os.makedirs("eob_uploads", exist_ok=True)
        with open(os.path.join("eob_uploads", eob_file.name), "wb") as f:
            f.write(eob_file.read())
        eob_uploaded = True

    # Message result
    if feedback_logged or eob_uploaded:
        st.success("✅ Thanks! We’ve received your input.")
    else:
        st.warning("⚠️ Please write feedback or upload a file before submitting.")
