# 🧠 OpsPilot (DuoOps) Model Fine-Tuning Guide

This folder contains everything needed to train and fine-tune a custom Google Gemini model for **OpsPilot**.

---

## 📁 Files in this Directory

* **`training_dataset.jsonl`**: The formatted JSONL dataset containing pairs of unstructured operational emails and their corresponding golden structured JSON outputs (entities, risk priority, intent, confidence, summary, recommended actions).
* **`generate_dataset.py`**: Python script to generate and augment `training_dataset.jsonl` with custom emails, internal SOP rules, client names, and specific risk policies.
* **`test_tuned_model.py`**: Diagnostic testing CLI script to run predictions and verify any tuned model before putting it into production.

---

## 🚀 How to Fine-Tune on Google AI Studio

Google AI Studio provides supervised fine-tuning for Gemini models directly from your web browser:

### Step 1: Open Google AI Studio
1. Navigate to **[aistudio.google.com](https://aistudio.google.com/)** and sign in with your Google account.
2. In the left navigation menu or top bar, click **"Create new"** $\rightarrow$ **"Tuned model"** (or go to [aistudio.google.com/tune](https://aistudio.google.com/tune)).

### Step 2: Upload Your Dataset
1. Choose **Import dataset**.
2. Select **Upload a file** and browse to:
   ```
   c:\Users\galam\Desktop\Projects\DuoOps\backend\training\training_dataset.jsonl
   ```
3. Set the columns:
   * **Input:** `text_input`
   * **Output:** `output`

### Step 3: Configure & Start Training
1. **Model:** Select a base model (e.g. `gemini-1.5-flash-001` or `gemini-2.0-flash`).
2. **Tuned Model Name:** e.g., `duoops-operations-analyst`
3. Click **"Tune model"**.
4. The training job will start. Depending on the size of the dataset, it typically takes 5–15 minutes.

### Step 4: Test Your Tuned Model
Once the training state shows **Active**, test it using the verification script:
```powershell
.\venv\Scripts\python.exe backend\training\test_tuned_model.py tunedModels/your-tuned-model-name
```

### Step 5: Activate in OpsPilot
In [`backend/.env`](file:///c:/Users/galam/Desktop/Projects/DuoOps/backend/.env), set:
```ini
GEMINI_MODEL=tunedModels/your-tuned-model-name
```
Restart your backend, and OpsPilot will now run exclusively on your custom-trained Gemini model!
