"""
数据库元数据配置管理模块

使用 YAML 文件存储数据库的物种、基因组版本、序列类型等元数据。
"""
import yaml
import os
from typing import Dict, Any, Optional

# Default to Docker path, but allow override via ENV
# In local development, we'll try to find it in the data directory
CONFIG_PATH = os.getenv("DATABASE_CONFIG_PATH", "/data/databases.yaml")

# Check fallback locations if the primary doesn't exist
FALLBACK_PATHS = [
    "/data/references/databases.yaml",
    "data/databases.yaml",
    "data/references/databases.yaml"
]

def get_actual_config_path() -> str:
    if os.path.exists(CONFIG_PATH):
        return CONFIG_PATH
    for path in FALLBACK_PATHS:
        if os.path.exists(path):
            return path
    return CONFIG_PATH



def load_config() -> Dict[str, Any]:
    """加载数据库配置"""
    path = get_actual_config_path()
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def save_config(config: Dict[str, Any]) -> None:
    """保存数据库配置"""
    path = get_actual_config_path()
    # 确保目录存在
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def get_db_metadata(db_id: str) -> Dict[str, Any]:
    """获取单个数据库元数据"""
    config = load_config()
    return config.get(db_id, {})


def update_db_metadata(db_id: str, metadata: Dict[str, Any]) -> None:
    """更新数据库元数据"""
    config = load_config()
    if db_id not in config:
        config[db_id] = {}
    config[db_id].update(metadata)
    save_config(config)


def delete_db_metadata(db_id: str) -> None:
    """删除数据库元数据"""
    config = load_config()
    if db_id in config:
        del config[db_id]
        save_config(config)
