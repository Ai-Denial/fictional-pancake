
# 🧾 AI Denial Appeal Generator

This Streamlit app helps medical billers and revenue cycle teams quickly generate professional insurance appeal letters for denied claims.

## ✨ Features

- Select common denial codes (e.g., CO-22, PR-204, CO-16, etc.)
- Automatically explains denial reasons, strategies, and evidence tips
- Payer-specific advice (e.g., Aetna, UHC, Medicare)
- Dynamic letter generation using OpenAI GPT-4
- Upload PDFs (EOBs, notes) and download merged appeal packet
- RARC (Remark Codes) and CARC pairings built-in
- Missing code logging for analytics

## 🛠️ How to Run

1. Clone the repository or copy the files
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key:
   ```
   export OPENAI_API_KEY="your-api-key"  # for Mac/Linux
   set OPENAI_API_KEY="your-api-key"     # for Windows
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

## 📁 Files

- `app.py` – Main Streamlit app
- `denial_codes.json` – Library of denial codes and RARC/payer strategies
- `requirements.txt` – Python dependencies
- `user_uploads/` – Folder where uploaded PDFs are saved
- `missing_codes.log` – Tracks which codes users searched but aren't in the database

## 💡 Sample Denial Codes Included

- CO-22: Bundled Service
- PR-204: Prior Authorization Missing
- CO-16: Missing Information
- OA-23: Not Medically Necessary
- N211: Duplicate Claim

## 💌 Feedback / Contributions

Email: [highswaad@gmail.com](mailto:highswaad@gmail.com)

## 🔒 Disclaimer

This tool is intended to assist with insurance appeal drafting. It is not a substitute for legal or medical billing advice. Always verify content before submitting to payers.
