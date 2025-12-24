# Synaptiq - Intelligent Local File Organizer

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PySide6](https://img.shields.io/badge/PySide6-Qt-green?style=for-the-badge&logo=qt)
![Llama 3.2](https://img.shields.io/badge/AI-Llama%203.2-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Synaptiq** is a modern, privacy-first desktop application that declutters your digital workspace. Standard organizers sort by file extension. Synaptiq sorts by context. It vectorizes your document content locally to identify semantic relationships, grouping related files - like a PDF invoice and a spreadsheet-budget regardless of format. An offline LLM then generates descriptive folder names for each cluster. No cloud APIs, no data leaks.

## 1. Synaptiq Dashboard
<img width="1247" height="676" alt="image" src="https://github.com/user-attachments/assets/c5e590c9-11a7-4f78-abad-83fdef76db06" />

## 2. Project Structure

```text
synaptiq/
├── models/             # Local GGUF models (downloaded here)
├── app.py              # Main Entry Point & PySide6 UI Logic
├── backend.py          # QThread Orchestrator (Signals & Slots)
├── worker.py           # Core AI Logic (Embeddings, Clustering, LLM)
├── constants.py        # Configuration (Model Paths, URLs)
└── requirements.txt    # Project Dependencies
```

## 3. Key Features

 - **AI Semantic Clustering**: Stop organizing by `Type` and start organizing by `Topic`. Synaptiq analyzes text within `PDFs`, `DOCX`, `PPTX`, and `TXT` files to group related documents together.
     - Example: Grouping a `Receipt.pdf` and `Budget.xlsx` into a `Financial_Records` folder.
 
 - **Local & Private**: Your data never leaves your device. Synaptiq utilizes optimized local models:
    - **Embeddings:** `all-MiniLM-L6-v2` (Sentence-Transformers)
    - **Reasoning:** `Llama-3.2-3B-Instruct` (GGUF via Llama.cpp)

 - **Smart Naming Engine**: No more generic folders like `Group_1`. The integrated LLM analyzes the cluster's contents and generates concise, professional folder names automatically
     - Example: `Project_Alpha_Specs`, `Travel_Itinerary_2024`.

 - **Hybrid Sorting Modes**: Switch instantly between AI and traditional logic:
   - **AI Semantic Cluster:** Deep content analysis.
   - **File Extension:** Groups by type `Images`, `Videos`, `Archives`.
   - **Date Modified:** Groups chronologically `Year-Month`.


## 4. Tech Stack

 -  **Interface:** [PySide6](https://pypi.org/project/PySide6/)
   
 -  **LLM Inference:** [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
   
 -  **Vector Search:** [sentence-transformers](https://huggingface.co/sentence-transformers) & [scikit-learn](https://scikit-learn.org/stable/) (Agglomerative Clustering)
 
 -  **Data Extraction:** `pypdf`, `python-docx`, `python-pptx`, `openpyxl`.

## 5. Installation

   - **Prerequisites**:
     - `Python 3.10` or higher.
     - **Windows Users:** Ensure [C++ Build Tools](https://visualstudio.microsoft.com/downloads/?q=build+tools) are installed (required for compiling `llama-cpp-python`).

   - **Steps**:

      -   **Clone the Repository**:
          ```bash
          git clone https://github.com/Adiii1436/synaptiq.git
          cd synaptiq
          ```
      
      -  **Create a Virtual Environment**:
          ```bash
          python -m venv venv
          
          # Windows:
          venv\Scripts\activate
          
          # Mac/Linux:
          source venv/bin/activate
          ```
      
      -  **Install Dependencies**:
          ```bash
          pip install -r requirements.txt
          ```
      
      -  **First Run**<br>
      
          Simply run the app. It will automatically download the required AI models (`Llama-3.2-3B` ~2GB and `MiniLM` ~90MB) on the first launch.
          ```bash
          python app.py
          ```

## 6. How It Works (AI Pipeline)

  - **Ingestion:** The system scans the target directory. Binary files (`Images`, `EXEs`) are sorted via hardcoded logic for speed.
    
  - **Extraction:** Readable documents (`PDF`, `DOCX`, `Code`) are parsed to extract text.
    
  - **Vectorization:** Text is converted into high-dimensional vectors using `SentenceTransformer`.
    
  - **Clustering:** `Agglomerative Clustering` groups vectors based on semantic similarity.
    
  - **Labeling:** The `Llama-3.2` model reads a summary of each cluster and generates a descriptive folder name.
