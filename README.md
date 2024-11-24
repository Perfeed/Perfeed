# 🚀 Perfeed
A personalized AI assistant tailored to streamline engineering team workflows.

## 🌟 Overview
Perfeed is an intelligent AI assistant designed to integrate seamlessly with engineering teams, making tasks like reviewing faster and more efficient. Struggling with a heavy workload and time-consuming reviews? Perfeed is here to help!

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

### Step-by-Step Setup

1. **Install Dependencies**  
   Run the following command in the root directory:  
   ```bash
   poetry install
   ```
   
2. **Configure Environment**:
    - Copy `perfeed/settings/.secrets_template.toml` file to `.secrets.toml`
    ```bash
    cp perfeed/settings/.secrets_template.toml perfeed/settings/.secrets.toml
    ```
    - Edit perfeed/settings/.secrets.toml and add the necessary values 
        - Github personal token, personal_access_token, is necessary. Please generate the token by going through the [Github doc](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
        - If you want to use OpenAI, a key is necessary. Please read the [OpenAI doc](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key)
    - (Optional) Update the values in perfeed/settings/configs.toml if you'd like to change the default configurations.

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