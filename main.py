# -*- coding: utf-8 -*-
import kivy

from kivy.app import App

from kivy.core.window import Window, Keyboard
from kivy.properties import ObjectProperty, StringProperty, ReferenceListProperty, NumericProperty, ListProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors.cover import CoverBehavior
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.button import Button
from kivy.atlas import Atlas
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.video import Video
from kivy.uix.videoplayer import VideoPlayer, VideoPlayerPreview
from kivy.uix.widget import Widget
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.animation import Animation
from kivy.event import EventDispatcher
from functools import partial
from kivy.uix.vkeyboard import VKeyboard
import unikeyboard
import tftp
import client
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
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header    import Header
from kivy.base import EventLoop
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


class MyText(TextInput, Keyboard):
    rootmanager = ObjectProperty()
    def __init__(self, **kwargs):
        super(MyText, self).__init__(**kwargs)

    def keyboard_on_key_up(self, window, key_str, * args):
        key = self.string_to_keycode(key_str)
        self.rootmanager.start()
        keycode = (key, key_str)
        k = self.interesting_keys.get(key)
        if k:
            key = (None, None, k, 1)
            self._key_up(key)


    def keyboard_on_key_down(self, window, key_str, text, modifiers):
        # Keycodes on OS X:
        ctrl, cmd = 64, 1024
        key = self.string_to_keycode(key_str)
        if key_str == 'ru':
            key=400
        if key_str == 'en':
            key=401
        if key_str == '123':
            key = 402

        keycode = (key, key_str)
        win = EventLoop.window

        # This allows *either* ctrl *or* cmd, but not both.
        is_shortcut = (modifiers == ['ctrl'])
        is_interesting_key = key in (list(self.interesting_keys.keys()) + [27, 400, 401, 402])

        if not self.write_tab and super(MyText,
                                        self).keyboard_on_key_down(window, key_str, text, modifiers):
            return True

        if not self._editable:
            # duplicated but faster testing for non-editable keys
            if text and not is_interesting_key:
                if is_shortcut and key == ord('c'):
                    self.copy()
            elif key == 27:
                self.focus = False
            return True

        if text and not is_interesting_key:

            self._hide_handles(win)
            self._hide_cut_copy_paste(win)
            win.remove_widget(self._handle_middle)

            # check for command modes
            # we use \x01INFO\x02 to get info from IME on mobiles
            # pygame seems to pass \x01 as the unicode for ctrl+a
            # checking for modifiers ensures conflict resolution.

            first_char = ord(text[0])
            if not modifiers and first_char == 1:
                self._command_mode = True
                self._command = ''
            if not modifiers and first_char == 2:
                self._command_mode = False
                self._command = self._command[1:]

            if self._command_mode:
                self._command += text
                return

            _command = self._command
            if _command and first_char == 2:
                from_undo = True
                _command, data = _command.split(':')
                self._command = ''
                if self._selection:
                    self.delete_selection()
                if _command == 'DEL':
                    count = int(data)
                    if not count:
                        self.delete_selection(from_undo=True)
                    end = self.cursor_index()
                    self._selection_from = max(end - count, 0)
                    self._selection_to = end
                    self._selection = True
                    self.delete_selection(from_undo=True)
                    return
                elif _command == 'INSERT':
                    self.insert_text(data, from_undo)
                elif _command == 'INSERTN':
                    from_undo = False
                    self.insert_text(data, from_undo)
                elif _command == 'SELWORD':
                    self.dispatch('on_double_tap')
                elif _command == 'SEL':
                    if data == '0':
                        Clock.schedule_once(lambda dt: self.cancel_selection())
                elif _command == 'CURCOL':
                    self.cursor = int(data), self.cursor_row
                return

            if is_shortcut:
                if key == ord('x'):  # cut selection
                    self._cut(self.selection_text)
                elif key == ord('c'):  # copy selection
                    self.copy()
                elif key == ord('v'):  # paste selection
                    self.paste()
                elif key == ord('a'):  # select all
                    self.select_all()
                elif key == ord('z'):  # undo
                    self.do_undo()
                elif key == ord('r'):  # redo
                    self.do_redo()
            else:
                if self._selection:
                    self.delete_selection()
                self.insert_text(text)
            # self._recalc_size()
            return

        if is_interesting_key:
            self._hide_cut_copy_paste(win)
            self._hide_handles(win)

        if key == 27:  # escape
            self.focus = False
            return True

        if key == 400: # йцукен
            self.keyboard.layout = 'json\\rukeyboard.json'
            return True

        if key == 401:  # qwerty
            self.keyboard.layout = 'json\\qwerty.json'
            return True

        if key == 402:  # bignumeric
            self.keyboard.layout = 'json\\bignum.json'
            return True

        elif key == 9:  # tab
            self.insert_text(u'\t')
            return True

        k = self.interesting_keys.get(key)
        if k:
            key = (None, None, k, 1)
            self._key_down(key)
    

class Manager(ScreenManager):

    login = StringProperty()
    password = StringProperty()
    access = ReferenceListProperty(login, password)

    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)
        Clock.schedule_interval(self.work_time, 25)

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
        now = datetime.now()
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
        with open('csv\\data.csv', newline='') as csvfile:
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
        now = datetime.now()
        date = f'{now:%d.%m.%Y}'
        anketa.append(date)
        # writer.writerow(anketa)
        with open('csv\\data.csv', 'w') as csvfile:
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
        # считываем файл в лист
        with open('csv\\review.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if row:
                    listing.append(row)
        # собираем инфу из текущей анкеты отзывов
        review = [self.ids.review1.ids.ank1q1.text,self.ids.review1.ids.ank1q2.text,self.ids.review1.ids.ank1q3.text,self.ids.review1.ids.ank1q4.text]
        review.append(self.ids.review2.ids.a4q1.text)
        now = datetime.now()
        date = f'{now:%d.%m.%Y}'
        review.append(date)
        listing.append(review)
        # дополняем лист с отзывами записываем в файл
        with open('csv\\review.csv', 'w') as csvfile:
            writer = csv.writer(csvfile,  delimiter=';', lineterminator = '\n')
            writer.writerows(listing)



    def work_time(self, dt):
        now = datetime.now()
        tt = now.timetuple()
        wd = tt[6] # 5-6 - выходные
        hr = tt[3]  # 8-18 - будем считать рабочими часами
        mn = tt[4]  # минуты для тестов
        if self.current == 'Language selection':
            if (mn//10)%2:
                self.ids['choice'].ids['logo'].source='img\\logo_white.png'
                self.ids['choice'].ids['buttonru'].color = [0.97, 0.43, 0.08, 1]
                self.ids['choice'].ids['buttonru'].canvas.before.children[0].rgb=[1, 1, 1]
                self.ids['choice'].ids['sreenchoicetexxt1'].color = [1, 1, 1, 1]
                self.ids['choice'].ids['podlozka'].canvas.children[0].rgba = [.3, .3, .3, .6]
            else:
                self.ids['choice'].ids['logo'].source='img\\logo_orange.png'
                self.ids['choice'].ids['buttonru'].color = [1, 1, 1, 1]
                self.ids['choice'].ids['buttonru'].canvas.before.children[0].rgb=[0.97, 0.43, 0.08]
                self.ids['choice'].ids['sreenchoicetexxt1'].color = [0.97, 0.43, 0.08, 1]
                self.ids['choice'].ids['podlozka'].canvas.children[0].rgba = [.3, .3, .3, .8]
            if wd < 5: # будний день
                if hr < 8 or hr >= 18:
                    self.current = 'Idle'
            else:
                self.current = 'Idle'

        if self.current == 'Idle':
            if wd < 5:  # будний день
                if hr >= 8 and hr < 18:
                    self.current = 'Language selection'

        
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
        manager.ids.wifiform.ids.imya_error.text = ''
        manager.ids.wifiform.ids.prtn_error.text = ''
        manager.ids.wifiform.ids.mail_error.text = ''


    def change_slide(self,index):
        for k, v in self.ids.items():
            if k[0:6] == 'slide_':
                try:
                    num_slider = int(k[6:]) #определяем номер 
                except:
                    print('неудалось преобразовать часть id в число')
                    num_slider = -1
                if num_slider == index:
                    v.background_normal = 'img\\dot_active.png'
                    v.background_down = 'img\\dot_active.png'
                else:
                    v.background_normal = 'img\\dot.png'
                    v.background_down = 'img\\dot.png'



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
            mail = self.ids.mail.text
        else:
            # TODO Тексты ошибок надо убрать в json и вытягивать значение для определённого языка
            self.ids.mail.background_color = [1, .7, .7, 1]
            if len(self.ids.mail.text):
                self.ids.mail_error.text = u'Укажите действительный адрес почты'
            else:
                self.ids.mail_error.text = u'Необходимо указать email'
            a = 0
        if len(self.ids.imya.text) >= 2:
            self.ids.imya.background_color = [1, 1, 1, 1]
            self.ids.imya_error.text = u''
            b = 1
            imya = self.ids.imya.text
        else:
            self.ids.imya.background_color = [1, .7, .7, 1]
            if len(self.ids.imya.text):
                self.ids.imya_error.text = u'Имя заполнено некорректно'
            else:
                self.ids.imya_error.text = u'Необходимо ввести ваше имя'
            b = 0
        if len(self.ids.prtn.text) >= 2:
            self.ids.prtn.background_color = [1, 1, 1, 1]
            self.ids.prtn_error.text = u''
            c = 1
            prtn = self.ids.prtn.text
        else:
            self.ids.prtn.background_color = [1, .7, .7, 1]
            if len(self.ids.prtn.text):
                self.ids.prtn_error.text = u'Наименование компании заполнено некорректно'
            else:
                self.ids.prtn_error.text = u'Необходимо ввести название компании'
            c = 0
        # Проверка на заполнение полей, если всё
        # нормально слать почту и генерить пароль
        # и перестраивать модельную форму
        if a+b+c == 3:
            manager.current = 'Access'
            manager.access = self.getconnect()
            login = manager.access[0]
            password = manager.access[1]
            now = datetime.now()
            date = f'{now:%d.%m.%Y}'
            time = f'{now:%H:%M}'
            wifiinfo = [imya, prtn, mail, login, password, date, time]
            ScreenWiFiForm.wifi_send_info('csv\\wifi.csv',wifiinfo)
            manager.start(420)
            # TODO В случае получения тапла с пустыпи логином и паролем, отрисовывать лейбл с информацией

    @staticmethod
    def getconnect():
        # tolist = App.get_running_app().config.get('mail','maillist').split(';')
        # smtp = App.get_running_app().config.get('mail','smtpip')
        # port = App.get_running_app().config.get('mail', 'smtpport')
        # sending = App.get_running_app().config.getint('mail', 'sendmail')
        # filepath = App.get_running_app().config.get('mail', 'filepath')
        # jsonfile = open(filepath, 'r')
        # logdict = json.load(jsonfile)
        # countpassword = len(logdict)
        # TODO Если countpassword меньше, например, пяти, то отсылать письмо админам, о том, что паролей осталось мало
        # jsonfile.close()
        # if logdict:
        # x=logdict.pop()
        pswd_list = ScreenWiFiForm.get_pswd()
        
        r = client.TFTPClient('192.168.64.5','69')
        try:
            r.write('pswd.txt', '/cbk/pswd.txt')
        except:
            login =''
            password=''
        del r

        try:
            os.remove(os.path.abspath('pswd.txt'))
        except:
            print('файла для удаления нет')
        
        login = pswd_list[0]
        password = pswd_list[1]
        # countpassword = pswd_list[2]
        # msg = u'\nLogin: {}\n  Password: {}'.format(login, password)
        # mail = MIMEText(msg, 'plain', 'utf-8')
        # mail['Subject'] = Header('Запрос пароля к Wi-Fi c iTable', 'utf-8')
        # mail['From'] = 'itable@uniflex.by'
        # mail['To'] = ", ".join(tolist)
        # if sending:
        #     try:
        #         s = smtplib.SMTP(smtp, port)
        #         s.starttls()
        #         s.sendmail(mail['From'], tolist, mail.as_string())
        #         s.quit()
        #     except:
        #         print('Не сработала отправка почты')
        # jsonfile = open(filepath, "w+")
        # jsonfile.write(json.dumps(logdict))
        # jsonfile.close()
        # else:
        #     login = ''
        #     password = ''

        return login, password

    @staticmethod
    def get_pswd():
        d = client.TFTPClient('192.168.64.5','69')
        d.read('/cbk/pswd.txt','pswd.txt')
        l = []
        login = ''
        counter = 0
        password = ''
        try:
            f = open('pswd.txt', 'r', encoding='utf-8')
            flag = True
            for line in f:
                row = line.split()
                if row[2] != '0' and flag:
                    login = row[0]
                    password = row[1]
                    row[2] = '0'
                    flag = False
                if row[2]!= '0':
                    counter = counter + 1
                l.append(row)
        except:
            print('Доступ к фалу пароле не получен')
        f = open('pswd.txt', 'w', encoding='utf-8')
        for row in l:
            f.write(' '.join(row)+'\n')
        f.close
        
        del d
        result = (login, password, counter)
        return result

    @staticmethod
    def wifi_send_info(file,listinfo):
        # TODO из 3ёх ф-ций, сделать одну с листом инфы и наим-ем файла
        listing = []
        # считываем файл в лист
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if row:
                    listing.append(row)
        # собираем инфу из формы перед выдачей доступа к wifi
        listing.append(listinfo)
        # дополняем лист с отзывами записываем в файл
        with open(file, 'w') as csvfile:
            writer = csv.writer(csvfile,  delimiter=';', lineterminator='\n')
            writer.writerows(listing)


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
    pass


class ScreenNewProduct(Screen):
    pass


class ScreenDigital(Screen):
    pass


class PrezDot(Button):
    sl = ObjectProperty()
    def __init__(self, **kwargs):
        super(PrezDot, self).__init__(**kwargs)


class PrezDotLine(BoxLayout):

    def __init__(self, **kwargs):
        super(PrezDotLine, self).__init__(**kwargs)
        

class PrezDotLineWrap(BoxLayout):
    
    def __init__(self, **kwargs):
        super(PrezDotLineWrap, self).__init__(**kwargs)


class PrezCarousel(Carousel):

    def on_index(self, *args):
        super(PrezCarousel, self).on_index(*args)
        main_layout=self.parent.parent
        Prez.change_slide(main_layout, self.index)
        main_layout.itable_manager.start()


class Prez(BoxLayout):
    folder = StringProperty()
    list_dots = ListProperty([])
    sl_carousel = ObjectProperty()
    short_name_for_id = StringProperty()
    itable_manager = ObjectProperty()

    def __init__(self, **kwargs):
        super(Prez, self).__init__(**kwargs)
        list_widgets = self.constructor('img\\prez_flexo\\', 'prez_', 1156, 750)
        for i in list_widgets:
            self.add_widget(i)

    def constructor(self, folder, short_name_for_id, width_slide, height_slide):
        dline = PrezDotLine()
        dwrap = PrezDotLineWrap()
        self.folder = folder
        self.short_name_for_id = short_name_for_id
        self.list_dots = []
        l = []
        for i in os.listdir(folder):
            if (i[-3:]) == 'jpg' or (i[-3:]) == 'png' or (i[-3:]) == 'gif':
                l.append(i)
        space = (width_slide - 26 * len(l)) // (len(l) - 1)
        if space > 16:
            space = 16
        if space < 0:
            space = 1
        dline.width = len(l) * 26 + len(l) * space
        slider = PrezCarousel()
        slider.size_hint = (None, None)
        slider.size = (width_slide, height_slide)
        slider.loop = True
        for i in os.listdir(folder):
            if (i[-3:]) == 'jpg' or (i[-3:]) == 'png' or (i[-3:]) == 'gif':
                src = f'{folder}{i}'
                image = AsyncImage(source=src, allow_stretch=True)
                slider.add_widget(image)
        self.sl_carousel = slider
        for i, item in enumerate(l):
            pd = PrezDot()
            txt = f'{short_name_for_id}{str(i)}'
            pd.id = txt
            pd.sl = slider
            if i == 0:
                pd.background_normal = 'img\\dot_active.png'
                pd.background_down = 'img\\dot_active.png'
            if i != 0:
                wd = Widget()
                wd.size_hint = (1, None)
                wd.width = space
                dline.add_widget(wd)
            pd.bind(on_release=self.change_sl)
            self.list_dots.append(pd)
            dline.add_widget(pd)
        dwrap.add_widget(Widget())
        dwrap.add_widget(dline)
        dwrap.add_widget(Widget())

        pcarouselwrap = BoxLayout(orientation = 'horizontal')
        pcarouselwrap.add_widget(Widget())
        pcarouselwrap.add_widget(slider)
        pcarouselwrap.add_widget(Widget())
        space = Widget(size_hint_y=None, height=60)
        result = [dwrap, pcarouselwrap, space]
        return result

    def change_sl(self,instance):
        len_name = len(self.short_name_for_id)
        num_slider = int(instance.id[len_name:])
        instance.sl.load_slide(instance.sl.slides[num_slider])

    def change_slide(self,index):
        for i, v in enumerate(self.list_dots):
            if index == i:
                v.background_normal = 'img\\dot_active.png'
                v.background_down = 'img\\dot_active.png'
            else:
                v.background_normal = 'img\\dot.png'
                v.background_down = 'img\\dot.png'

    def load_prev(self):
        self.sl_carousel.load_previous()

    def load_next(self):
        self.sl_carousel.load_next()


class PrezNewProduct(BoxLayout):

    def __init__(self, **kwargs):
        super(PrezNewProduct, self).__init__(**kwargs)
        list_widgets = Prez.constructor(self,'img\\prez_new\\', 'preznew_', 1156, 750)
        for i in list_widgets:
            self.add_widget(i)

    def change_sl(self, instance):
        len_name = len(self.short_name_for_id)
        num_slider = int(instance.id[len_name:])
        instance.sl.load_slide(instance.sl.slides[num_slider])


class PrezDigital(BoxLayout):

    def __init__(self, **kwargs):
        super(PrezDigital, self).__init__(**kwargs)
        list_widgets = Prez.constructor(
            self, 'img\\prez_digital\\', 'prez_d_', 1156, 750)
        for i in list_widgets:
            self.add_widget(i)

    def change_sl(self, instance):
        len_name = len(self.short_name_for_id)
        num_slider = int(instance.id[len_name:])
        instance.sl.load_slide(instance.sl.slides[num_slider])


class PrezMain(BoxLayout):

    def __init__(self, **kwargs):
        super(PrezMain, self).__init__(**kwargs)
        list_widgets = Prez.constructor(
            self, 'img\\prez_main\\', 'prez_m_', 1200, 410)
        self.add_widget(list_widgets[0])
        self.add_widget(list_widgets[1])
        wd = list_widgets[2]
        wd.height = 99
        self.add_widget(wd)

    def change_sl(self, instance):
        len_name = len(self.short_name_for_id)
        num_slider = int(instance.id[len_name:])
        instance.sl.load_slide(instance.sl.slides[num_slider])


class Booklet(BoxLayout):
    def __init__(self, **kwargs):
        super(Booklet, self).__init__(**kwargs)
        list_widgets = Prez.constructor(
            self, 'img\\buklet\\', 'b_', 1440, 720)
        self.add_widget(list_widgets[0])
        self.add_widget(list_widgets[1])
        wd = list_widgets[2]
        wd.height = 40
        self.add_widget(wd)

    def change_sl(self, instance):
        len_name = len(self.short_name_for_id)
        num_slider = int(instance.id[len_name:])
        instance.sl.load_slide(instance.sl.slides[num_slider])


class ScreenVideo(Screen):
    
    def exit_video(self):
        self.ids.vplay.children[0].play = False
        self.ids.vplay.children[0].state = 'stop'
    
    def rewind_video(self):
        st = self.ids.vframe.state
        if self.ids.vframe.state != 'stop':
            pr = round(self.ids.vscale.get_norm_value(),3)
            self.ids.vframe.seek(pr)
    def rewind_video_down(self):
        print(self)


    def play_video(self):
        if self.ids.vframe.state == 'play':
            self.ids.vframe.state = 'pause'
            self.ids.voverlay.background_normal = 'img\\video_pause.png'
            self.ids.voverlay.background_down = 'img\\video_pause.png'
            self.ids.vplaypause.background_normal = 'img\\video_player\\play.png'
            self.ids.vplaypause.background_down = 'img\\video_player\\play.png'
        else:
            self.ids.vframe.state = 'play'
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
                self.video.duration = 511
            else:
                seek = self.video.position / self.video.duration
        # convert to minutes:seconds
        d = self.video.duration * seek
        minutes = int(d / 60)
        seconds = int(d - (minutes * 60))
        # fix bubble label & position
        self.bubble_label.text = '%d:%02d' % (minutes, seconds)
        self.bubble.center_x = self.x + seek * self.width
        self.bubble.y = self.top+6

    def _showhide_bubble(self, instance, value):
        if value == 'play':
            self._hide_bubble()
        else:
            self._show_bubble()


class Vid(Video):

    def __init__(self, **kwargs):
        super(Vid, self).__init__(**kwargs)


class ScreenIdle(Screen):
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
        now = datetime.now()
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
