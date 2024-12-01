# 🚀 Perfeed
A personalized AI assistant tailored to streamline engineering team workflows.

## 🌟 Overview
Perfeed is an intelligent AI assistant designed to integrate seamlessly with engineering teams, making tasks like reviewing faster and more efficient. Struggling with a heavy workload and time-consuming reviews? Perfeed is here to help!

## Features
Currently, Perfeed offers a key feature: summarizing pull requests to generate a comprehensive weekly summary. More features are on the way, driven by user feedback and feature requests. Stay tuned for updates!

## ⚙️ Getting Started

### Prerequisites

1. **Python**  
   - Install Python 3.10 or higher.  
   - **Recommendation**: Use a [Conda virtual environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) for managing Python versions.

2. **Poetry**  
   - Install **Poetry 1.8.3**, the package manager used to handle Python dependencies. Dependencies are listed in the `pyproject.toml` file.  
   - Installation:  
     ```bash
     curl -sSL https://install.python-poetry.org | python3 - --version 1.8.3
     ```

## Step-by-Step Setup

Follow these steps to set up and configure the project.

### **1. Install Dependencies**  
   Run the following command in the root directory:  
   ```bash
   poetry install
   ```

### **2. Configure Environment**

#### Add Github Secrets:
- Edit the file `perfeed/settings/.secrets.toml` and provide the necessary values:
  - GitHub Personal Token (`personal_access_token`):  
    Generate a token by following the GitHub Personal Access Token Guide at [https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

---

### **3. Optional: Use Ollama (Local Model)**

If you prefer to run a local model to protect your data, follow these steps:

#### Copy the Template:
Copy the `.secrets_template.toml` file to `.secrets.toml` by renaming the file in the settings folder.
   ```bash
   cp perfeed/settings/.secrets_template.toml perfeed/settings/.secrets.toml
   ```

#### Install Ollama:
Install Ollama by following the instructions in the Ollama Installation Guide at [https://ollama.com/download](https://ollama.com/download).

#### Download and Run a Model:
- Browse the Ollama Model List at [https://ollama.com/search](https://ollama.com/search) and choose a model to download.
- Follow the specific instructions provided for running the selected model.

#### Update Configuration:
Specify the downloaded model version under the ollama_model setting in the perfeed/settings/configs.toml file.

---

### **3. Optional: Use ChatGPT (OpenAI Models)**

To use ChatGPT via OpenAI's API, follow these steps:

#### Copy the Template:
Rename the `.secrets_template.toml` file to `.secrets.toml` in the settings folder.
   ```bash
   cp perfeed/settings/.secrets_template.toml perfeed/settings/.secrets.toml
   ```

#### Add an OpenAI API Key:
Obtain an API key from OpenAI by following the OpenAI API Key Guide at [https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key).

#### Setup the model version
Update `openai_model` in `perfeed/settings/configs.toml` with the model you want. Here's the [list](https://platform.openai.com/docs/models).

### **4. Update Configuration**:
Specify the variables for Ollama you wish to use in the `perfeed/settings/configs.toml` file.

---

Now your setup is complete, and you can begin using the project!

##  Execution 
We use the jupyter notebook to do the summary. Here are the steps:
1. Please go through the `perfeed/notebooks/weekly_summary.ipynb` notebook with the example.

2. In the root folder, run the command below and it would redirect you to the browser.
   ```bash
   jupyter notebook perfeed/notebooks/weekly_summary.ipynb
   ```

   Or you can see the localhost in the terminal after running the cmd. Please paste the URL in the browser, and you can see the notebook.

3. Update the repo owner and the repo you want in the notebook via browser, and execute. 
   - Here's the way to find the Owner Repo, and the Author name. Here's the example PR URL: `https://github.com/Perfeed/perfeed/pull/29`
      - Owner: `Perfeed`
      - Repo: `perfeed` 
      - Author name: `jzxcd`