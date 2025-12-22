import os
from pathlib import Path
from dataclasses import dataclass


def parse_yaml(file_path: Path) -> dict:
    config = {}
    current_section = None
    
    if not file_path.exists():
        return config
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            
            if not line or line.strip().startswith('#'):
                continue
            
            if not line.startswith(' ') and line.endswith(':'):
                current_section = line[:-1].strip()
                config[current_section] = {}
            elif current_section and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                if value.isdigit():
                    value = int(value)
                elif value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                
                config[current_section][key] = value
    
    return config


@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000


@dataclass  
class StorageConfig:
    file: str = "data/tasks.txt"


@dataclass
class Config:
    server: ServerConfig
    storage: StorageConfig
    
    @classmethod
    def load(cls, config_path: Path = None) -> "Config":
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yml"
        
        yaml_config = parse_yaml(config_path)
        
        server_cfg = yaml_config.get('server', {})
        storage_cfg = yaml_config.get('storage', {})
        
        return cls(
            server=ServerConfig(
                host=os.getenv('HOST', server_cfg.get('host', '127.0.0.1')),
                port=int(os.getenv('PORT', server_cfg.get('port', 8000)))
            ),
            storage=StorageConfig(
                file=os.getenv('TASKS_FILE', storage_cfg.get('file', 'data/tasks.txt'))
            )
        )
