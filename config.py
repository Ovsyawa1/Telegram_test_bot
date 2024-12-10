import os
from configparser import ConfigParser
from dotenv import load_dotenv

load_dotenv()

config = ConfigParser()
config.read("config.ini")

BOT_TOKEN = os.getenv("BOT_TOKEN", config.get(section="bot", option="token", fallback=None))
if not BOT_TOKEN:
    exit("Provide BOT_TOKEN!")


SAYONARA_CHECK = ["до свидания", "пока"]

DOGS_PIC_URL = "https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"

DOG_PIC_FILE_ID = "AgACAgIAAxkDAAO6ZrIafo8TDI2Y8fIdu-Ms8Z4st3EAAhzgMRt0ypFJ3GLko8dlHUsBAAMCAAN3AAM1BA"

W_PICK_FILE_ID = "AgACAgIAAxkBAAIBiGbE2kQBkr8bClLwfxUapoCa9XqjAAIS4DEbq7QoSo3apC0Wxps8AQADAgADeQADNQQ"

def get_admin_ids():
    admin_ids = config.get(section="admin", option="admin_ids", fallback="")
    admin_ids = [admin_id.strip() for admin_id in admin_ids.split(",")]
    admin_ids = [
        int(admin_id)
        for admin_id in admin_ids
        if admin_id
    ]
    return admin_ids

ADMIN_LIST = get_admin_ids