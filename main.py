# -*- coding: utf-8 -*-
import kivy

from kivy.app import App

from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors.cover import CoverBehavior
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.video import Video
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from functools import partial
from kivy.properties import *
import unikeyboard
import re
import conf
import json
import smtplib
import sys
import os
import codecs
import timer
from email.mime.text import MIMEText
from email.header    import Header

# TODO: ADD: Клавиатура к форме выыдачи доступа к WiFi
# TODO: ADD: Форма анкеты на выдачу доступа к WiWi: кнопка отправить
# TODO: ADD: Организовать подгрузку текста из JSON файла на выбранном языке из первой формы
# TODO: Окно с данными доступа к Wifi
# TODO: Настроить отправщик почты с кириллицей

glob_tim = ObjectProperty(None)

class ScreenMenu(Screen):

    def open_wifi_form(self, manager):
        global glob_tim
        manager.current = 'FormAccess'
        manager.ids.wifiform.ids.imya.text = ''
        manager.ids.wifiform.ids.prtn.text = ''
        manager.ids.wifiform.ids.mail.text = ''
        manager.ids.wifiform.ids.imya.background_color = [1, 1, 1, 1]
        manager.ids.wifiform.ids.prtn.background_color = [1, 1, 1, 1]
        manager.ids.wifiform.ids.mail.background_color = [1, 1, 1, 1]



    def uni_text_b(self,lang,interface):
        filepath=os.getcwd()+'\\json\\text.json'
        jsonfile = codecs.open(filepath, 'r','utf-8')
        logdict = json.load(jsonfile)
        jsonfile.close()
        try:
            return(logdict[interface][lang])
        except:
            return ('!%%%%%!')



class ScreenBuklet(Screen):
    pass


class ScreenVideo(Screen):
    pass


class ScreenWiFiForm(Screen):

    def sendmail(self, manager):

        print(self.ids.imya.text)
        print(self.ids.prtn.text)
        print(self.ids.mail.text)
        if re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', self.ids.mail.text):
            self.ids.mail.background_color = [1, 1, 1, 1]
            a = 1
        else:
            self.ids.mail.background_color = [1, .7, .7, 1]
            a = 0
        if len(self.ids.imya.text) >= 2:
            self.ids.imya.background_color = [1, 1, 1, 1]
            b = 1
        else:
            self.ids.imya.background_color = [1, .7, .7, 1]
            b = 0
        if len(self.ids.prtn.text) >= 2:
            self.ids.prtn.background_color = [1, 1, 1, 1]
            c = 1
        else:
            self.ids.prtn.background_color = [1, .7, .7, 1]
            c = 0
        # Проверка на заполнение полей, если всё
        # нормально слать почту и генерить пароль
        # и перестраивать модельную форму
        if a+b+c == 3:
            manager.current = 'Access'
            manager.access = self.getconnect()





    def getconnect(self):
        tolist = ['smarkov@uniflex.by','nyankovskaya@a.uniflex.by']
        jsonfile = open('pswd.json', 'r')
        logdict = json.load(jsonfile)
        self.login = ''
        self.password = ''
        jsonfile.close()
        ind = -1
        for i, x in enumerate(logdict):
            if x['used'] == 1:
                self.login = x['login']
                self.password = x['password']
                msg = "\n\n\nLogin: {}\n  Password: {}".format(self.login, self.password)
                # self.loginpassword.text = msg
                # self.add_widget(self.algpw)
                mail = MIMEText(msg,'plain','utf-8')
                mail['Subject'] = Header('Запрос пароля к Wi-Fi c iTable','utf-8')
                mail['From'] = 'itable@uniflex.by'
                mail['To'] = ", ".join(tolist)

                ind = i
                break
            else:
                continue
        else:
            self.login = ''
            self.password = ''
        # s = smtplib.SMTP('192.168.64.5', '25')
        # s.starttls()
        # s.sendmail(mail['From'], tolist, mail.as_string())
        # s.quit()
        if ind != -1:
            logdict[ind]['used'] = 0
            jsonfile = open("pswd.json", "w+")
            jsonfile.write(json.dumps(logdict))
            jsonfile.close()
        return (self.login,self.password)


class ScreenWiFiInfo(Screen):
    pass



class Manager(ScreenManager):

    login = StringProperty()
    password = StringProperty()
    access = ReferenceListProperty(login, password)

    def my_callback(self,dt):
        if self.current=='Access':
            self.current = 'Menu'
            self.start()
        else:
            self.current='Language selection'


    def start(self):
        global glob_tim
        try:
            glob_tim.cancel()
        except:
            print('нет таймера')
        glob_tim=Clock.schedule_once(self.my_callback, 120)



class LangButton(Button):
    pass


class FormInput(TextInput):
    pass


class WiFiButton(Button):

    def __init__(self, **kwargs):
        super(WiFiButton, self).__init__(**kwargs)
        self.size_hint = (0.5, None)
        self.height = 100
        self.text = 'Получить доступ к Wi-Fi'
        self.font_size = 32


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


class ScreensApp(App):
    interface_lang = StringProperty()

    def uni_text(self,lang,interface):
        filepath=os.getcwd()+'\\json\\text.json'
        jsonfile = codecs.open(filepath, 'r','utf-8')
        logdict = json.load(jsonfile)
        jsonfile.close()
        try:
            return(logdict[interface][lang])
        except:
            return ('!%%%%%!')

    def build(self):
        return Manager()



if __name__ == '__main__':
    ScreensApp().run()
