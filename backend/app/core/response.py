from typing import Any, Optional


def success(data: Any = None, message: str = "ok"):
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error(message: str = "error", code: int = 500):
    return {
        "success": False,
        "message": message,
        "code": code,
        "data": None
    }