# -*- coding: utf-8 -*-
import kivy

from kivy.app import App

from kivy.core.window import Window
from kivy.properties import *
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors.cover import CoverBehavior
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.button import Button
from kivy.atlas import Atlas
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.video import Video
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from functools import partial
import unikeyboard
import re
import json
import smtplib
import sys
import os
import codecs
import timer
import win32net
from datetime import datetime as dt
from email.mime.text import MIMEText
from email.header    import Header

# TODO: ADD: Клавиатура к форме выыдачи доступа к WiFi
# TODO: ADD: Форма анкеты на выдачу доступа к WiWi: кнопка отправить
# TODO: ADD: Организовать подгрузку текста из JSON файла на выбранном языке из первой формы
# TODO: Окно с данными доступа к Wifi
# TODO: Настроить отправщик почты с кириллицей

glob_tim = ObjectProperty(None)


class Manager(ScreenManager):

    login = StringProperty()
    password = StringProperty()
    access = ReferenceListProperty(login, password)

    def my_callback(self, dt):
        if self.current == 'Access':
            self.current = 'Menu'
            self.start()
        else:
            self.current = 'Language selection'


    def start(self):
        global glob_tim
        try:
            glob_tim.cancel()
        except:
            print('нет таймера')
        glob_tim = Clock.schedule_once(self.my_callback, 120)


class ScreenMenu(Screen):

    @staticmethod
    def open_wifi_form(manager):
        global glob_tim
        manager.current = 'FormAccess'
        manager.ids.wifiform.ids.imya.text = ''
        manager.ids.wifiform.ids.prtn.text = ''
        manager.ids.wifiform.ids.mail.text = ''
        manager.ids.wifiform.ids.imya.background_color = [1, 1, 1, 1]
        manager.ids.wifiform.ids.prtn.background_color = [1, 1, 1, 1]
        manager.ids.wifiform.ids.mail.background_color = [1, 1, 1, 1]


class ScreenBuklet(Screen):
    pass


class ScreenVideo(Screen):
    pass


class ScreenWiFiForm(Screen):

    def __init__(self, **kwargs):
        super(ScreenWiFiForm, self).__init__(**kwargs)
        self.login = ''
        self.password = ''

    def sendmail(self, manager):

        if re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', self.ids.mail.text):
            self.ids.mail.background_color = [1, 1, 1, 1]
            self.ids.mail_error.text = u''
            a = 1
        else: # TODO Тексты ошибок надо убрать в json и вытягивать значение для определённого языка
            self.ids.mail.background_color = [1, .7, .7, 1]
            if len(self.ids.mail.text):
                self.ids.mail_error.text = u'e-mail заполнен некорректно'
            else:
                self.ids.mail_error.text = u'Необходимо заполнить e-mail'
            a = 0
        if len(self.ids.imya.text) >= 2:
            self.ids.imya.background_color = [1, 1, 1, 1]
            self.ids.imya_error.text = u''
            b = 1
        else:
            self.ids.imya.background_color = [1, .7, .7, 1]
            if len(self.ids.imya.text):
                self.ids.imya_error.text = u'Имя заполнено некорректно'
            else:
                self.ids.imya_error.text = u'Необходимо ввести Ваше имя'
            b = 0
        if len(self.ids.prtn.text) >= 2:
            self.ids.prtn.background_color = [1, 1, 1, 1]
            self.ids.prtn_error.text = u''
            c = 1
        else:
            self.ids.prtn.background_color = [1, .7, .7, 1]
            if len(self.ids.prtn.text):
                self.ids.prtn_error.text = u'Наименование организации заполнено некорректно'
            else:
                self.ids.prtn_error.text = u'Необходимо заполнить наименование Вашей организации'
            c = 0
        # Проверка на заполнение полей, если всё
        # нормально слать почту и генерить пароль
        # и перестраивать модельную форму
        if a+b+c == 3:
            manager.current = 'Access'
            manager.access = self.getconnect()
            # TODO В случае получения тапла с пустыпи логином и паролем, отрисовывать лейбл с информацией

    @staticmethod
    def getconnect():
        tolist = App.get_running_app().config.get('mail','maillist').split(';')
        smtp = App.get_running_app().config.get('mail','smtpip')
        port = App.get_running_app().config.get('mail', 'smtpport')
        sending = App.get_running_app().config.getint('mail', 'sendmail')
        filepath = App.get_running_app().config.get('mail', 'filepath')
        jsonfile = open(filepath, 'r')
        logdict = json.load(jsonfile)
        countpassword = len(logdict)
        # TODO Если countpassword меньше, например, пяти, то отсылать письмо админам, о том, что паролей осталось мало
        jsonfile.close()
        if logdict:
            x=logdict.pop()
            login = x['login']
            password = x['password']
            date = x['date']
            msg = "\nLogin: {}\n  Password: {}".format(login, password)
            mail = MIMEText(msg, 'plain', 'utf-8')
            mail['Subject'] = Header('Запрос пароля к Wi-Fi c iTable', 'utf-8')
            mail['From'] = 'itable@uniflex.by'
            mail['To'] = ", ".join(tolist)
            if sending:
                try:
                    s = smtplib.SMTP(smtp, port)
                    s.starttls()
                    s.sendmail(mail['From'], tolist, mail.as_string())
                    s.quit()
                except:
                    print('Не сработала отправка почты')
            jsonfile = open(filepath, "w+")
            jsonfile.write(json.dumps(logdict))
            jsonfile.close()
        else:
            login = ''
            password = ''

        return login, password


class ScreenWiFiInfo(Screen):
    pass


class ScreenChoice(CoverBehavior, Video, AnchorLayout, Screen):
    """Видео в фоне"""

    def _on_video_frame(self, *largs):
        self._video.eos = 'loop'
        video = self._video
        if not video:
            return
        texture = video.texture
        self.reference_size = texture.size
        self.calculate_cover()
        self.duration = video.duration
        self.position = video.position
        self.texture = texture
        self.anchor_x = 'center'
        self.anchor_y = 'center'
        self.canvas.ask_update()


class ScreenAnketa1(Screen):
    pass


class ScreenAnketa2(Screen):
    pass


class ScreenAnketa3(Screen):
    pass


class ScreenAnketa4(Screen):
    pass


class ScreenAnketa5(Screen):
    pass


class ScreensApp(App):
    interface_lang = StringProperty()

    @staticmethod
    def uni_text(lang, interface):
        filepath = os.getcwd() + '\\json\\text.json'
        jsonfile = codecs.open(filepath, 'r', 'utf-8')
        logdict = json.load(jsonfile)
        jsonfile.close()
        try:
            return(logdict[interface][lang])
        except:
            return ('!%%%%%!')

    def log_using(self, current):
        now = dt.now()
        print(f'[{now:%d.%m.%Y %H:%M}] start screen {current}')

    def build(self):
        config = self.config
        return Manager()

    def build_config(self, config):
        config.setdefaults('mail', {'smtpip': '192.168.0.1',
                                    'smtpport': '42',
                                    'maillist': 'mail@domain.com; mail2@domain.com',
                                    'filepath': '',
                                    'sendmail': '0'})


if __name__ == '__main__':
    ScreensApp().run()
