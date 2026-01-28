import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
TEXTS_PATH = BASE_DIR / "data" / "texts.json"

_texts_cache = None


def load_texts():
    global _texts_cache
    if _texts_cache is None:
        with TEXTS_PATH.open("r", encoding="utf-8") as f:
            _texts_cache = json.load(f)
    return _texts_cache


def get_text(key: str, default: str = "") -> str:
    texts = load_texts()
    return texts.get(key, default)


async def get_text_with_admin(key: str, db, default: str = "") -> str:
    """
    Textni olish va {admin_username} ni bazadan admin username bilan almashtirish.

    JSON da shunday yozing: "... {admin_username} ga yuboring."
    Natija: "... @real_admin_username ga yuboring."
    """
    texts = load_texts()
    text = texts.get(key, default)

    # Agar {admin_username} bo'lsa, bazadan olish
    if "{admin_username}" in text:
        admins = await db.get_admins()
        if admins and len(admins) > 0:
            # Birinchi adminning username'ini olish
            # admin_users jadvalida: id, username
            admin_username = admins[0][1]  # index'ni tekshiring!
            if admin_username:
                # @ belgisi yo'q bo'lsa qo'shish
                if not admin_username.startswith("@"):
                    admin_username = f"@{admin_username}"
                text = text.replace("{admin_username}", admin_username)

    return text


def set_text(key: str, value: str) -> None:
    texts = load_texts()
    texts[key] = value
    with TEXTS_PATH.open("w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    # invalidate cache so subsequent reads get updated content
    global _texts_cache
    _texts_cache = None