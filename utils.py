import yaml
from typing import Dict, Any
import os


def load_config(config_path: str = "config.yaml") -> Dict[Any, Any]:
    """
    读取配置文件

    Args:
        config_path (str): 配置文件路径，默认为 "config.yaml"

    Returns:
        Dict[Any, Any]: 配置文件内容的字典表示

    Raises:
        FileNotFoundError: 当配置文件不存在时
        yaml.YAMLError: 当配置文件格式错误时
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            return config
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"配置文件解析错误: {e}")


# 使用示例
if __name__ == "__main__":
    try:
        config = load_config()
        print("服务器配置:")
        print(f"  IP: {config['server']['ip']}")
        print(f"  端口: {config['server']['port']}")
        print(f"  传输协议: {config['server']['transport']}")

        print("\n工具配置:")
        for tool in config["tools"]:
            print(f"  工具名称: {tool['name']}")
            print(f"  描述: {tool['description']}")
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"错误: {e}")
