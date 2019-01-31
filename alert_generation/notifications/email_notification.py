from mlogging import logger
from abc import ABC, abstractmethod
from typing import List, Type, Dict
from postgresql_init import engine
from sqlalchemy.sql import text
from notification import Notification
import smtplib, ssl


class EmailNotification(Notification):
    def __init__(self, user_to_notify: int):
        self.user_to_notify = user_to_notify

    def notify(self):
        with engine.begin() as conn:
            s = text("SELECT * FROM REGISTERED_USER WHERE user_pk=:user_to_notify")
            result = conn.execute(s, user_to_notify=self.user_to_notify)

            for row in result:
                email = row['email']
                logger.info('Sending email notification to email {}'.format(email))
                EmailNotification.send_email(email)


    @staticmethod
    def get_all_from_db(alert_pk: int) -> List[Notification]:
        ret: List[Notification] = []

        with engine.begin() as conn:
            s = text("select * from EMAIL_NOTIFICATION WHERE notify_on_which_alert = :notify_on_which_alert")
            result = conn.execute(s, notify_on_which_alert=alert_pk)
            
            for row in result:
                notification = EmailNotification(row['user_to_notify'])
                notification.notification_pk = row['notification_pk']
                notification.notify_on_which_alert = row['notify_on_which_alert']
                ret.append(notification)

        return ret

    @staticmethod
    def send_email(email: str):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login('crypto.observatory@gmail.com', 'tidux2284da06')
            server.sendmail('crypto.observatory@gmail.com', email, 'Your alert has been fired off')