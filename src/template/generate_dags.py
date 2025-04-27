import json
from pathlib import Path 
import os

from jinja2 import Template

def main():

    with open("./template.py", "r", encoding="utf-8") as file:
        unsafe_template_str = file.read()

    folder_configs = Path("./dag_configs/")
    print(f"folder_configs {folder_configs}")
    
    dags_dir = "./../dags"
    
    for path_config in folder_configs.glob("config_*.json"):
        with open(path_config, "r", encoding="utf-8") as file:
            config = json.load(file)

        template_str = protect_undefineds(unsafe_template_str, config)
        
        filename = f"{dags_dir}/{config['dag_name']}.py"

        content = Template(template_str).render(config)
        
        with open(filename, mode="w", encoding="utf-8") as file:
            file.write(content)
            print(f"Created {filename} from config: {path_config.name}...")

if __name__ == "__main__":
    main()

