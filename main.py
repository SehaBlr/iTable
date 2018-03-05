# -*- coding: utf-8 -*-
import kivy

from kivy.app import App

from kivy.core.window import Window
from kivy.properties import ObjectProperty,StringProperty,ReferenceListProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors.cover import CoverBehavior
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.button import Button
from kivy.atlas import Atlas
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.video import Video
from kivy.uix.videoplayer import VideoPlayer, VideoPlayerPreview
from kivy.clock import Clock
from functools import partial
import unikeyboard
import re
import json
import smtplib
import sys
import os
import codecs
import csv
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
# Оранжевый  - 250, 110,  20
# Серый      - 149, 179, 179
# Графитовый -  77,  77,  77

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

    def start(self, ret=120):
        global glob_tim
        try:
            glob_tim.cancel()
        except:
            pass
        glob_tim = Clock.schedule_once(self.my_callback, ret)

    def anketa_clear_info(self):
        for v in self.ids.anketa1.ids:
            try:
                self.ids.anketa1.ids[v].text = ''
            except:
                pass
        for v in self.ids.anketa2.ids:
            try:
                self.ids.anketa2.ids[v].active = False
            except:
                pass
        for v in self.ids.anketa3.ids:
            try:
                self.ids.anketa3.ids[v].active = False
            except:
                pass
        self.ids.anketa3.ids.anketa3q8.value = 0
        self.ids.anketa4.ids.a4q1.text = ''
        self.ids.anketa5.ids.a5q1.text = ''

    def anketa_send_info(self):
        listing=[]
        with open('data.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if row:
                    listing.append(row)


        anketa = [self.ids.anketa1.ids.ank1q1.text,self.ids.anketa1.ids.ank1q2.text,self.ids.anketa1.ids.ank1q3.text,self.ids.anketa1.ids.ank1q4.text]
        anketa.append(self.anketa_product())
        for i in range(2,9):
            t = f'q{str(i)}'
            anketa.append(self.anketa_satisfy(t))
        for i in range(1,8):
            t = f'q0{str(i)}'
            anketa.append(self.anketa_change(t))
        anketa.append(str(int((self.ids.anketa3.ids.anketa3q8.value)/20)))
        anketa.append(self.ids.anketa4.ids.a4q1.text)
        anketa.append(self.ids.anketa5.ids.a5q1.text)
        listing.append(anketa)
        # writer.writerow(anketa)
        print(listing)
        with open('data.csv', 'w') as csvfile:
            writer = csv.writer(csvfile,  delimiter=';', lineterminator = '\n')
            writer.writerows(listing)

    def anketa_product(self):
        prod = ''
        if self.ids.anketa2.ids.anketa2q1r1.active:
            prod += ScreensApp.uni_text('RU','anketa2q1r1') + ', '
        if self.ids.anketa2.ids.anketa2q1r2.active:
            prod += ScreensApp.uni_text('RU','anketa2q1r2') + ', '
        if self.ids.anketa2.ids.anketa2q1r3.active:
            prod += ScreensApp.uni_text('RU','anketa2q1r3') + ', '
        if self.ids.anketa2.ids.anketa2q1r4.active:
            prod += ScreensApp.uni_text('RU','anketa2q1r4') + ', '
        return prod

    def anketa_satisfy(self, group):
        prod = ''
        dd = {}
        for k, v in self.ids.anketa2.ids.items():
            if k[2:4] == group:
                if v.active:
                    name_scores = f'anketa2{k[4:6]}'
                    prod = ScreensApp.uni_text('RU', name_scores)
        return prod

    def anketa_change(self, group):
        prod = ''
        dd = {}
        for k, v in self.ids.anketa3.ids.items():
            if k[2:5] == group:
                if v.active:
                    name_scores = f'anketa3{k[5:7]}'
                    prod = ScreensApp.uni_text('RU', name_scores)
        return prod


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
        else:
            # TODO Тексты ошибок надо убрать в json и вытягивать значение для определённого языка
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


class ScreenAnketaThanks(Screen):
    pass


class ScreenReview1(Screen):
    pass


class ScreenReview2(Screen):
    pass


class ScreenReviewThanks(Screen):
    pass


class ScreenBooklet(Screen):
    pass


class ScreenVideo(Screen):
    


    def exit_video(self):
        self.ids.vplay.children[0].play = False
        self.ids.vplay.children[0].state = 'stop'
        

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

    def change_current(self,screen_name):
        self.root.current = screen_name
        self.root.start()

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
