import os
import requests
import logging
import zipfile
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


# SITE_URL = "https://www.jobvector.com"
SITE_URL = "https://github.com/pureYu"
EMAIL_ADDRESS = os.environ.get('GM_EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('GM_EMAIL_PASS')
EMAIL_RECIPIENT = EMAIL_ADDRESS
EMAIL_SERVER = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_SUBJECT = "YOUR SITE IS DOWN!"
EMAIL_BODY = "Make shure the server is restarted and it is back up. Find log file attached."

now = datetime.now()
PATH_LOG_DIR = "_log"
PATH_LOG_FILE = f"{PATH_LOG_DIR}/{now:%Y%m%d}.log"
PATH_LOG_ZIPFILE = f"{PATH_LOG_DIR}/log_{now:%Y%m%d}.zip"


logging.basicConfig(filename=PATH_LOG_FILE,
                    # level=logging.INFO,
                    level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(message)s',
                    datefmt = '%H:%M:%S %m/%d/%Y')


def notify_user():
    """  SEND EMAIL ABOUT CRUSH  """
    with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        msg = MIMEMultipart()
        msg['Subject'] = EMAIL_SUBJECT
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_RECIPIENT
        msg.attach(MIMEText(EMAIL_BODY, 'plain'))

        attachment_file = None
        try:
            zip(PATH_LOG_FILE, PATH_LOG_ZIPFILE)
        except Exception:
            pass

        if os.path.isfile(PATH_LOG_ZIPFILE):
            attachment_file = PATH_LOG_ZIPFILE
        elif os.path.isfile(PATH_LOG_FILE):
            attachment_file = PATH_LOG_FILE
        else:
            attachment_file = None

        if (attachment_file):
            part = MIMEBase("application", "octet-stream")
            part.set_payload(open(attachment_file, "rb").read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename=\"{os.path.basename(attachment_file)}\"")
            msg.attach(part)


        logging.info('Sending email')
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

        if os.path.isfile(PATH_LOG_ZIPFILE):
            logging.info(f'Deleting ZIP archive - {PATH_LOG_ZIPFILE}')
            os.remove(PATH_LOG_ZIPFILE)


def zip(src, zip_filename):
    if os.path.isfile(src):
        logging.info(f'Creating ZIP archive from {src}')
        zip_file = zipfile.ZipFile(zip_filename, "w")
        abs_name = os.path.abspath(src)
        arc_name = os.path.basename(src)
        # zf.write(abs_name, arc_name)
        zip_file.write(abs_name, arc_name)
        zip_file.close()


try:
    r = requests.get(SITE_URL, timeout=5)
    if r.status_code != 200:
        logging.exception(f'Website is DOWN! 1 http status code = {r.status_code}')
        notify_user()
    else:
        logging.info('Website is UP')
except Exception as e:
    logging.exception(f'Website is DOWN! 2 {e}')
    notify_user()


# # Run cron-job:
# () $ which   # смотрим, какое virtual env активно
# /Users/pure/dev/python/site_monitor/monitor_env/bin/python
# () $ ~/dev/python/site_monitor/monitor_env/bin/python
# Python 3.7.2 (v3.7.2:9a3ffc0492, Dec 24 2018, 02:44:43)
# ...
# >>> import requests
# >>> exit()
# () $ ~/dev/python/site_monitor/monitor_env/bin/python ~/dev/python/site_monitor/monitor.py
