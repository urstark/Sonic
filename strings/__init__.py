import os
import re
import logging
from typing import List, Dict, Any, Tuple

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sonic.Strings")

languages: Dict[str, Dict[str, str]] = {}
languages_clean: Dict[str, Dict[str, str]] = {}
languages_present: Dict[str, str] = {}

class LanguageDict(dict):
    """Custom dict that allows getting clean strings for buttons."""
    def __init__(self, data: Dict[str, str], clean_data: Dict[str, str]):
        super().__init__(data)
        self.clean_data = clean_data

    def __getitem__(self, key: str) -> Any:
        return self.get(key, "")

    def __call__(self, key: str, clean: bool = False) -> str:
        if clean:
            return self.clean_data.get(key, self.get(key, ""))
        return str(self.get(key, ""))

def get_string(lang: str) -> LanguageDict:
    if lang not in languages:
        lang = "en"
    return LanguageDict(languages[lang], languages_clean[lang])

def inject_emojis(lang_dict: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str]]:
    try:
        emojis_path = r"./strings/emojis.yml"
        if not os.path.exists(emojis_path):
            logger.warning(f"Emojis file not found at {emojis_path}")
            return {k: str(v) for k, v in lang_dict.items()}, {k: str(v) for k, v in lang_dict.items()}
            
        with open(emojis_path, "r", encoding="utf8") as f:
            emojis = yaml.safe_load(f)
            
        if not emojis:
            logger.warning("Emojis file is empty")
            return {k: str(v) for k, v in lang_dict.items()}, {k: str(v) for k, v in lang_dict.items()}
            
        clean_dict = {}
        processed_dict = {}
        
        # Inject emojis as top-level keys so they can be accessed as _["emo_key"]
        for emo_key, emo_val in emojis.items():
            processed_dict[emo_key] = str(emo_val)
            clean_dict[emo_key] = "" # Buttons get NO emojis
            
        # Process language strings
        for key, val in lang_dict.items():
            if isinstance(val, str):
                temp_val = val
                temp_clean = val
                for emo_key, emo_val in emojis.items():
                    # Processed dict gets the full emoji (premium or fallback)
                    temp_val = temp_val.replace(f"{{{emo_key}}}", str(emo_val))
                    # Clean dict gets NOTHING for emojis (no icons at all on buttons)
                    temp_clean = temp_clean.replace(f"{{{emo_key}}}", "").strip()
                
                # Further cleanup for buttons: remove any leftover HTML tags if any
                temp_clean = re.sub(r"<.*?>", "", temp_clean).strip()
                # Remove extra spaces that might result from stripping emojis
                temp_clean = re.sub(r"\s+", " ", temp_clean)

                processed_dict[key] = temp_val
                clean_dict[key] = temp_clean
            else:
                processed_dict[key] = str(val)
                clean_dict[key] = str(val)
                
        return processed_dict, clean_dict
    except Exception as e:
        logger.error(f"Error in inject_emojis: {e}", exc_info=True)
        return {k: str(v) for k, v in lang_dict.items()}, {k: str(v) for k, v in lang_dict.items()}

# Load base
en_path = r"./strings/langs/en.yml"
if os.path.exists(en_path):
    try:
        with open(en_path, "r", encoding="utf8") as f:
            en_raw = yaml.safe_load(f)
        if not en_raw:
            en_raw = {}
        languages["en"], languages_clean["en"] = inject_emojis(en_raw)
        languages_present["en"] = str(languages["en"].get("name", "English"))
        logger.info("Loaded English language strings")
    except Exception as e:
        logger.error(f"Failed to load English strings: {e}", exc_info=True)

# Load others
langs_dir = r"./strings/langs/"
if os.path.exists(langs_dir):
    for filename in os.listdir(langs_dir):
        if filename.endswith(".yml") and filename != "en.yml":
            lang_name = filename[:-4]
            try:
                with open(os.path.join(langs_dir, filename), "r", encoding="utf8") as f:
                    raw_data = yaml.safe_load(f)
                
                if not raw_data:
                    raw_data = {}

                # Inherit from English (raw strings first, then inject)
                # This ensures missing keys in translations use English versions with emojis
                with open(en_path, "r", encoding="utf8") as f:
                    final_raw = yaml.safe_load(f) or {}
                final_raw.update(raw_data)
                
                languages[lang_name], languages_clean[lang_name] = inject_emojis(final_raw)
                languages_present[lang_name] = str(raw_data.get("name", lang_name))
                logger.info(f"Loaded language: {lang_name}")
            except Exception as e:
                logger.error(f"Error loading language {filename}: {e}", exc_info=True)

if "en" not in languages:
    # Critical fallback
    languages["en"] = {"name": "English"}
    languages_clean["en"] = {"name": "English"}
    languages_present["en"] = "English"
    logger.critical("English language failed to load! Using empty strings.")
