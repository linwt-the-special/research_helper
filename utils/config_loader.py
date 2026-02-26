import yaml
import os
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_path: str = "configs/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """获取特定智能体的模型配置"""
        agents_config = self.config.get("agents", {})
        if agent_name not in agents_config:
            raise ValueError(f"智能体 '{agent_name}' 在配置中未定义")
        return agents_config[agent_name]

    def get_settings(self) -> Dict[str, Any]:
        """获取全局设置"""
        return self.config.get("settings", {})

# 全局单例
config_loader = ConfigLoader()
