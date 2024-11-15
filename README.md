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
    - Copy perfeed/settings/.secrets_template.toml file to .secrets.toml
    ```bash
    cp perfeed/settings/.secrets_template.toml perfeed/settings/.secrets.toml
    ```
    - Edit perfeed/settings/.secrets.toml and add the necessary values (e.g., API keys, secrets).
    - (Optional) Update the values in perfeed/settings/configs.toml if you'd like to change the default configurations.

# Execution 
