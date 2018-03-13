# -*- coding: utf-8 -*-
import kivy

from kivy.app import App

from kivy.core.window import Window
from kivy.properties import ObjectProperty,StringProperty,ReferenceListProperty, NumericProperty
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
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.animation import Animation
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
import time
import win32net
from datetime import datetime as dt, timedelta
from email.mime.text import MIMEText
from email.header    import Header
from kivy.uix.slider import Slider

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
        now = dt.now()
        minute = int(ret//60)
        print(f'[{now:%d.%m.%Y %H:%M}] таймер сброшен на {minute} минуты')
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

    def review_clear_info(self):
        for v in self.ids.review1.ids:
            try:
                self.ids.review1.ids[v].text = ''
            except:
                pass
        self.ids.review2.ids.a4q1.text = ''

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

    def review_send_info(self):
        listing=[]
        with open('review.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if row:
                    listing.append(row)


        review = [self.ids.review1.ids.ank1q1.text,self.ids.review1.ids.ank1q2.text,self.ids.review1.ids.ank1q3.text,self.ids.review1.ids.ank1q4.text]
        review.append(self.ids.review2.ids.a4q1.text)
        listing.append(review)
        print(listing)
        with open('review.csv', 'w') as csvfile:
            writer = csv.writer(csvfile,  delimiter=';', lineterminator = '\n')
            writer.writerows(listing)


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
    
    def change_slide(self,index):
        for k, v in self.ids.items():
            if k[0:5] == 'slide':
                try:
                    num_slider = int(k[5:]) #определяем номер 
                except:
                    print('неудалось преобразовать часть id в число')
                    num_slider = -1
                if num_slider == index:
                    v.background_normal = 'img\\dot_active.png'
                    v.background_down = 'img\\dot_active.png'
                else:
                    v.background_normal = 'img\\dot.png'
                    v.background_down = 'img\\dot.png'



class ScreenSolution(Screen):

    def change_slide(self,index):
        for k, v in self.ids.items():
            if k[0:5] == 'prez_':
                try:
                    num_slider = int(k[5:]) #определяем номер 
                except:
                    print('неудалось преобразовать часть id в число')
                    num_slider = -1
                if num_slider == index:
                    v.background_normal = 'img\\dot_active.png'
                    v.background_down = 'img\\dot_active.png'
                else:
                    v.background_normal = 'img\\dot.png'
                    v.background_down = 'img\\dot.png'


class ScreenVideo(Screen):
    

    def exit_video(self):
        self.ids.vplay.children[0].play = False
        self.ids.vplay.children[0].state = 'stop'
    
    # def callback(self,dt):
    #     # print(self.event)
    #     print(time.strftime("%M:%S", time.gmtime(self.ids.vframe.position)))

    def rewind_video(self):
        st = self.ids.vframe.state
        print (st)
        if self.ids.vframe.state != 'stop':
            pr = round(self.ids.vscale.get_norm_value(),3)
            self.ids.vframe.seek(pr)
            # self.ids.vframe.state= 'pause'
            # self.ids.vframe.position = (self.ids.vscale.get_norm_value()) * (self.ids.vframe.duration)
            # self.ids.vframe.state = st
    def rewind_video_down(self):
        print(self)


    def play_video(self):
        if self.ids.vframe.state == 'play':
            self.ids.vframe.state = 'pause'
            # print(time.strftime("%M:%S", time.gmtime(self.ids.vframe.position)))
            # print(time.strftime("%M:%S", time.gmtime(self.ids.vframe.duration)))
            # print(self.ids.vframe.loaded)
            self.ids.voverlay.background_normal = 'img\\video_pause.png'
            self.ids.voverlay.background_down = 'img\\video_pause.png'
            self.ids.vplaypause.background_normal = 'img\\video_player\\play.png'
            self.ids.vplaypause.background_down = 'img\\video_player\\play.png'
        else:
            self.ids.vframe.state = 'play'
            # print(self.ids.vframe.duration)
            # print(self.ids.vframe.position)
            self.ids.voverlay.background_normal = 'img\\px.png'
            self.ids.voverlay.background_down = 'img\\px.png'
            self.ids.vplaypause.background_normal = 'img\\video_player\\pause.png'
            self.ids.vplaypause.background_down = 'img\\video_player\\pause.png'

    def stop_video(self):
        if self.ids.vframe.state != 'stop':
            self.ids.vframe.state = 'stop'
            self.ids.vframe.posotion = 0
            self.ids.vframe.loaded = False
            self.ids.vplaypause.background_normal = 'img\\video_player\\play.png'
            self.ids.vplaypause.background_down = 'img\\video_player\\play.png'
            self.ids.voverlay.background_normal = 'img\\video_start.png'
            self.ids.voverlay.background_down = 'img\\video_start.png'


class SliBar(ProgressBar):
    video = ObjectProperty(None)
    seek = NumericProperty(None, allownone=True)
    alpha = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(SliBar, self).__init__(**kwargs)
        self.bubble = Factory.Bubble(size=(50, 44))
        self.bubble_label = Factory.Label(text='0:00')
        self.bubble.add_widget(self.bubble_label)
        self.add_widget(self.bubble)

        update = self._update_bubble
        fbind = self.fbind
        fbind('pos', update)
        fbind('size', update)
        fbind('seek', update)

    def on_video(self, instance, value):
        self.video.bind(position=self._update_bubble,
                        state=self._showhide_bubble)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        self._show_bubble()
        touch.grab(self)
        self._update_seek(touch.x)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        self._update_seek(touch.x)
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        if self.seek:
            self.video.seek(self.seek)
        self.seek = None
        self._hide_bubble()
        return True

    def _update_seek(self, x):
        if self.width == 0:
            return
        x = max(self.x, min(self.right, x)) - self.x
        self.seek = x / float(self.width)

    def _show_bubble(self):
        self.alpha = 1
        Animation.stop_all(self, 'alpha')

    def _hide_bubble(self):
        self.alpha = 1.
        Animation(alpha=0, d=4, t='in_out_expo').start(self)

    def on_alpha(self, instance, value):
        self.bubble.background_color = (1, 1, 1, value)
        self.bubble_label.color = (1, 1, 1, value)

    def _update_bubble(self, *l):
        seek = self.seek
        if self.seek is None:
            if self.video.duration == 0:
                seek = 0
            else:
                seek = self.video.position / self.video.duration
        # convert to minutes:seconds
        d = self.video.duration * seek
        minutes = int(d / 60)
        seconds = int(d - (minutes * 60))
        # fix bubble label & position
        self.bubble_label.text = '%d:%02d' % (minutes, seconds)
        self.bubble.center_x = self.x + seek * self.width
        self.bubble.y = self.top

    def _showhide_bubble(self, instance, value):
        if value == 'play':
            self._hide_bubble()
        else:
            self._show_bubble()



class Vid(Video):

    def __init__(self, **kwargs):
        super(Vid, self).__init__(**kwargs)


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
