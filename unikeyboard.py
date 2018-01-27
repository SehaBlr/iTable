from kivy.uix.button import Button
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.stacklayout import StackLayout
from kivy.event import EventDispatcher
from kivy.properties import *
from itertools import cycle

class UniKeyboard(StackLayout):

    mem_focus=StringProperty()
    current_lang=StringProperty('EN')
    num_keyboard=BooleanProperty(False)
    tablist=ListProperty([])
    keyaction=ListProperty([u'\u0531', u'\u2936', '123', 'RU', 'EN', u'\u232B','ABC'])

class Key(Button,FocusBehavior,EventDispatcher):

    key_text = ListProperty([])

    def press_key(self,rootids,keytext):
        for k,v in rootids:
            try:
                if v.focus:
                    self.parent.mem_focus=v.hint_text
                    break
            except:
                pass
        else:
            self.parent.mem_focus=''
        if keytext==u'\u0531' and self.parent.num_keyboard==False:
            if self.parent.current_lang == 'RU':
                for i in self.parent.children:
                    i.text = i.key_text[3]
            if self.parent.current_lang == 'EN':
                for i in self.parent.children:
                    i.text = i.key_text[1]
        if keytext not in self.parent.keyaction:
            try:
                if len(v.selection_text):
                    v.delete_selection()
            except Exception as e:
                print(e)
        if keytext == u'\u232B':
            try:
                if len(v.selection_text):
                    v.delete_selection()
                else:
                    v.text = v.do_backspace()
            except:
                pass


    def key_up(self,keytext,rootids):
        """Ищем среди проиндексированных клаасов, те, у которых фокус равен сохранненному в global_a"""
        for k, v in rootids:
            try:
                if v.hint_text==self.parent.mem_focus:
                    if keytext not in self.parent.keyaction: #если это обычная клавиша, то плюсуем значение в поле
                        pos1=v.cursor[0]
                        if pos1>=len(v.text):
                            aftercursor=''
                        else:
                            aftercursor=v.text[pos1:]
                        if pos1==0:
                            beforecursor=''    
                        else:
                            beforecursor=v.text[0:pos1]
                        # res=v.text+keytext
                        res=beforecursor+keytext+aftercursor
                        v.text=res
                        v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был
                        v.cursor=(pos1+1,0)
                    else:
                        if keytext == u'\u232B':
                            v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был

                        if keytext == u'\u2936':
                            print(self.parent.tablist)
                            print(v.hint_text)
                            for i in self.parent.tablist:
                                if i == v.hint_text:
                                    print(i)
                                    j = self.parent.tablist.index(i)
                                    print(j)
                                    if self.parent.tablist[-1]!=i:
                                        print(self.parent.tablist[j+1])
                                        if self.focus_by_hint_text(self.parent.tablist[j+1], rootids):
                                            break
                                    else:
                                        print(self.parent.tablist[0])
                                        if self.focus_by_hint_text(self.parent.tablist[0], rootids):
                                            break
                            else:
                                print('Цикл ничего не нашёл')
                                v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был
                                # if i == v.hint_text:
                                #     print (self.parent.tablist[i])


                            # if v.hint_text=='Организация':
                            #     if self.focus_by_hint_text('email',rootids):
                            #         break
                            # if v.hint_text=='email':
                            #     if self.focus_by_hint_text('Имя',rootids):
                            #         break
                            # if v.hint_text=='Имя':
                            #     if self.focus_by_hint_text('Организация',rootids):
                            #         break
                        elif keytext==u'\u0531' and self.parent.num_keyboard==False:
                            if self.parent.current_lang == 'RU':
                                for i in self.parent.children:
                                    i.text = i.key_text[2]
                            if self.parent.current_lang == 'EN':
                                for i in self.parent.children:
                                    i.text = i.key_text[0]
                            v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был
                        else:
                            self.change_lang(keytext)
                            v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был
                    break
                else:  #если элементов с фокусум не найдено, то ничего не делаем
                    pass
            except: # фокус не нашли, значит работаем с самой клавой - меняем раскладки
                self.change_lang(keytext)

    def focus_by_hint_text(self,hint,rootids):
        for k, v in rootids:
            try:
                if v.hint_text==hint:
                    v.focus = True
                    v.select_all()
                    return True
                    break
            except:
                pass
        else:
            return False

    def change_lang(self,keytext):
        if keytext == 'RU':
            for i in self.parent.children:
                i.text = i.key_text[2]
            self.parent.num_keyboard=False
            self.parent.current_lang = keytext
        if keytext == 'EN':
            for i in self.parent.children:
                i.text = i.key_text[0]
            self.parent.num_keyboard=False
            self.parent.current_lang = keytext
        if keytext == '123':
            self.parent.num_keyboard = True
            for i in self.parent.children:
                if i.text == 'RU' or i.text == 'EN':
                    continue
                i.text = i.key_text[4]
        if keytext == 'ABC':
            self.parent.num_keyboard = False
            for i in self.parent.children:
                if self.parent.current_lang == 'RU':
                    i.text = i.key_text[2]
                if self.parent.current_lang == 'EN':
                    i.text = i.key_text[0]
        if keytext == u'\u0531' and self.parent.num_keyboard == False:
            if self.parent.current_lang == 'RU':
                for i in self.parent.children:
                    i.text = i.key_text[2]
            if self.parent.current_lang == 'EN':
                for i in self.parent.children:
                    i.text = i.key_text[0]


