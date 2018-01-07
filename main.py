import kivy

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors.cover import CoverBehavior
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.video import Video
from kivy.graphics.instructions import Canvas
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from functools import partial
from kivy.core.window import Window
import json
import smtplib

Window.fullscreen = True
width = 2560
height = 1440
Window.size = (width, height)

# TODO: 1.Форма анкеты
# TODO: 2.Второе модельное окно для запроса инфы на Wi-Fi

Config.set('kivy','keyboard_mode','')
Config.write()

class ScreenMenu(Screen):
    pass


class ScreenBuklet(Screen):
    pass


class ScreenVideo(Screen):
    pass


class ScreenWiFiForm(Screen):
    pass

class ScreenWiFiInfo(Screen):
    pass

class Manager(ScreenManager):
    pass


class LangButton(Button):
    pass


class FormInput(TextInput):
    pass


class ModalLayout(BoxLayout):

    def __init__(self, **kwargs):
        super(ModalLayout, self).__init__(**kwargs)


class WiFiView(ModalView):

    def __init__(self, **kwargs):
        super(WiFiView, self).__init__(**kwargs)



    def on_dismiss(self):
        print(type(self.children[0].clearform))
        # self.children[0].clearform()
        #
        # try:
        #     self.children[0].remove_widget(self.aname)
        # except:
        #     pass
        # try:
        #     self.children[0].remove_widget(self.aprtn)
        # except:
        #     pass
        # try:
        #     self.children[0].remove_widget(self.amail)
        # except:
        #     pass
        # try:
        #     self.children[0].remove_widget(self.header)
        # except:
        #     pass
        # try:
        #     self.children[0].remove_widget(self.abutton)
        # except:
        #     pass

    def on_open(self):
        print(self.children[0])
        # self.children[0].fname.text = ''
        # self.children[0].fprtn.text = ''
        # self.children[0].fmail.text = ''
        # try:
        #     self.children[0].add_widget(self.header)
        # except:
        #     self.children[0].remove_widget(self.header)
        #     self.children[0].add_widget(self.header)
        # try:
        #     self.children[0].add_widget(self.aname)
        # except:
        #     pass
        # try:
        #     self.children[0].add_widget(self.aprtn)
        # except:
        #     pass
        # try:
        #     self.children[0].add_widget(self.amail)
        # except:
        #     pass
        # try:
        #     self.children[0].add_widget(self.abutton)
        # except:
        #     pass

# class WiFiInput(BoxLayout):
#
#     def __init__(self, **kwargs):
#         super(WiFiInput, self).__init__(**kwargs)
#
#         self.orientation = 'vertical'
#         self.spacing = 15
#         self.padding = [25, ]
#
#         self.fname = FormInput(hint_text='Имя', padding_x=23, padding_y=12)
#         self.fprtn = FormInput(hint_text='Организация', padding_x=23, padding_y=12)
#         self.fmail = FormInput(hint_text='e-mail', padding_x=23, padding_y=12)
#         self.aname = AnchorLayout(anchor_x='center')
#         self.aprtn = AnchorLayout(anchor_x='center')
#         self.amail = AnchorLayout(anchor_x='center')
#         self.algpw = AnchorLayout(anchor_x='center', anchor_y='center')
#         self.aclos = RelativeLayout(size_hint=(1, None), height=1)
#
#         self.bclos = Button(text='×', size_hint=(None, None), size=(25, 25), pos=(1100,-36))
#
#         self.abutton = AnchorLayout(anchor_x='center')
#         self.header = Label(text='Заполниwте форму', size_hint=(1, None), height=45)
#         self.wbutton = WiFiButton()
#         self.loginpassword = Label(font_size=32, font_name='font\\PT_Sans-Web-Regular')
#         self.algpw.add_widget(self.loginpassword)
#
#         self.aname.add_widget(self.fname)
#         self.wbutton.bind(on_press=self.sendmail)
#         self.aprtn.add_widget(self.fprtn)
#         self.amail.add_widget(self.fmail)
#         self.abutton.add_widget(self.wbutton)
#         self.aclos.add_widget(self.bclos)
#
#         self.add_widget(self.aclos)
#         self.add_widget(self.header)
#         self.add_widget(self.aname)
#         self.add_widget(self.aprtn)
#         self.add_widget(self.amail)
#         self.add_widget(self.abutton)
#
#     def sendmail(self, instance):
#         print(self.fname.text)
#         print(self.fprtn.text)
#         print(self.fmail.text)
#         # Проверка на заполнение полей, если всё
#         # нормально слать почту и генерить пароль
#         # и перестраивать модельную форму
#         self.remove_widget(self.aname)
#         self.remove_widget(self.aprtn)
#         self.remove_widget(self.amail)
#         self.remove_widget(self.header)
#         self.remove_widget(self.abutton)
#         self.getconnect()
#
#     def getconnect(self):
#
#         jsonfile = open('pswd.json', 'r')
#         logdict = json.load(jsonfile)
#         jsonfile.close()
#         ind = -1
#         for i, x in enumerate(logdict):
#             if x['used'] == 1:
#                 msg = "Логин: {}\n\nПароль: {}".format(x['login'], x['password'])
#                 self.loginpassword.text = msg
#                 self.add_widget(self.algpw)
#                 ind = i
#                 break
#             else:
#                 continue
#         if ind != -1:
#             logdict[ind]['used'] = 0
#             jsonfile = open("pswd.json", "w+")
#             jsonfile.write(json.dumps(logdict))
#             jsonfile.close()
#         # self.clearform()
#
#
#     def clearform(self):
#         self.fname.text = ''
#         self.fprtn.text = ''
#         self.fmail.text = ''
#
#     def startform(self):
#         self.add_widget(self.header)
#         self.add_widget(self.aname)
#         self.add_widget(self.aprtn)
#         self.add_widget(self.amail)
#         self.add_widget(self.abutton)



class WiFiButton(Button):

    def __init__(self, **kwargs):
        super(WiFiButton, self).__init__(**kwargs)
        self.size_hint = (0.5, None)
        self.height = 100
        self.text = 'Получить доступ к Wi-Fi'
        self.font_size = 32


class ScreenChoise(CoverBehavior, Video, AnchorLayout, Screen):
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


class ScreensApp(App):

    # def build_config(self, config):
    #     config.setdefaults('graphics', {
    #         'height': '1920',
    #         'width': '1080'
    res_heigth = height
    res_width = width
    #     })

    def build(self):
        # config = self.config
        return Manager()


if __name__ == '__main__':
    ScreensApp().run()
