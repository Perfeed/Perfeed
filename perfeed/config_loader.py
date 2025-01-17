import os
from dynaconf import Dynaconf

current_dir = os.path.dirname(os.path.abspath(__file__))
settings = Dynaconf(
    settings_files=[
        os.path.join(current_dir, f)
        for f in [
            "settings/.secrets.toml",
            "settings/configs.toml",
            "settings/pr_summary_prompts.toml",
            "settings/weekly_summary_prompts.toml",
        ]
    ]
)
