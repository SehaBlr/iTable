from kivy.uix.button import Button
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.stacklayout import StackLayout
from kivy.event import EventDispatcher
from kivy.properties import *
from itertools import cycle

class UniKeyboard(StackLayout):

    mem_focus=StringProperty()
    current_lang=StringProperty('RU')
    num_keyboard=BooleanProperty(False)
    tablist=ListProperty([])
    idslist = ListProperty([])
    keyaction=ListProperty([u'\u0531', u'\u2936', '123', 'RU', 'EN', u'\u232B','ABC'])
    upper=BooleanProperty(True)

class Key(Button,FocusBehavior,EventDispatcher):

    key_text = ListProperty([])

    def press_key(self,keytext):
        for k,v in self.parent.idslist:
            try:
                if v.focus:
                    self.parent.mem_focus=k
                    break
            except:
                pass
        else:
            self.parent.mem_focus=''
        if keytext==u'\u0531' and self.parent.num_keyboard==False:
            if self.parent.upper:
                if self.parent.current_lang == 'RU':
                    for i in self.parent.children:
                        i.text = i.key_text[2]
                if self.parent.current_lang == 'EN':
                    for i in self.parent.children:
                        i.text = i.key_text[0]
                self.parent.upper=False
            else:
                if self.parent.current_lang == 'RU':
                    for i in self.parent.children:
                        i.text = i.key_text[3]
                if self.parent.current_lang == 'EN':
                    for i in self.parent.children:
                        i.text = i.key_text[1]
                self.parent.upper = True
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


    def key_up(self,keytext):
        """Ищем среди проиндексированных классов, те, у которых фокус равен сохранненному в global_a"""
        for k, v in self.parent.idslist:
            try:
                if k==self.parent.mem_focus:
                    if keytext not in self.parent.keyaction: #если это обычная клавиша, то плюсуем значение в поле
                        col=v.cursor_col
                        row=v.cursor_row
                        print(col)
                        print(row)
                        print(f'{len(v.text)} символов')
                        pos1 = 0
                        if row>0:
                            start = 0
                            for i in range(0, row):
                                pos1 = v.text.find('\n',start)
                                start = pos1+1
                        pos1 = pos1 +1+ col  
                        print(f'Позиция курсора -- {pos1}')
                        if pos1>=len(v.text):
                            aftercursor=''
                        else:
                            aftercursor=v.text[pos1:]
                        if pos1==0:
                            beforecursor=''    
                        else:
                            beforecursor=v.text[0:pos1]
                        # res=v.text+keytext
                        print(beforecursor)
                        print(f'------{keytext}------')
                        print(aftercursor)
                        res=beforecursor+keytext+aftercursor
                        v.text=res
                        v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был
                        v.cursor=(col+1,row)
                        if self.parent.upper and self.parent.num_keyboard==False:
                            if self.parent.current_lang == 'RU':
                                for i in self.parent.children:
                                    i.text = i.key_text[2]
                            if self.parent.current_lang == 'EN':
                                for i in self.parent.children:
                                    i.text = i.key_text[0]
                            self.parent.upper = False
                    else:
                        if keytext == u'\u232B':
                            v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был

                        if keytext == u'\u2936':
                            for i in self.parent.tablist:
                                if i == k:
                                    j = self.parent.tablist.index(i)
                                    if self.parent.tablist[-1]!=i:
                                        if self.focus_by_hint_text(self.parent.tablist[j+1]):
                                            break
                                    else:
                                        if self.focus_by_hint_text(self.parent.tablist[0]):
                                            break
                            else:
                                col=v.cursor[0]
                                row=v.cursor[1]
                                start = 0
                                pos1 = 0
                                for i in range(0, row):
                                    pos1 = v.text.find('\n', start)
                                    start = pos1 + 1
                                pos1 = pos1 + 1 + col
                                if pos1>=len(v.text):
                                    aftercursor=''
                                else:
                                    aftercursor=v.text[pos1:]
                                if pos1==0:
                                    beforecursor=''    
                                else:
                                    beforecursor=v.text[0:pos1]
                                # res=v.text+keytext
                                res=beforecursor+'\n'+aftercursor
                                v.text=res
                                v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был
                                v.cursor=(0,row+1)
                        elif keytext==u'\u0531' and self.parent.num_keyboard==False:
                            # if self.parent.current_lang == 'RU':
                            #     for i in self.parent.children:
                            #         i.text = i.key_text[2]
                            # if self.parent.current_lang == 'EN':
                            #     for i in self.parent.children:
                            #         i.text = i.key_text[0]
                            v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был
                        else:
                            self.change_lang(keytext)
                            v.focus = True  # при любом раскладе пытаемся сохранить фокус, если он был
                    break
                else:  #если элементов с фокусум не найдено, то ничего не делаем
                    pass
            except: # фокус не нашли, значит работаем с самой клавой - меняем раскладки
                self.change_lang(keytext)

    def focus_by_hint_text(self,hint):
        for k, v in self.parent.idslist:
            try:
                if k==hint:
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
            self.parent.upper = False
            for i in self.parent.children:
                i.text = i.key_text[2]
            self.parent.num_keyboard=False
            self.parent.current_lang = keytext
        if keytext == 'EN':
            self.parent.upper=False
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
            self.parent.upper = False
            for i in self.parent.children:
                if self.parent.current_lang == 'RU':
                    i.text = i.key_text[2]
                if self.parent.current_lang == 'EN':
                    i.text = i.key_text[0]
        if keytext == u'\u0531' and self.parent.num_keyboard == False:
            if self.parent.upper:
                if self.parent.current_lang == 'RU':
                    for i in self.parent.children:
                        i.text = i.key_text[3]
                if self.parent.current_lang == 'EN':
                    for i in self.parent.children:
                        i.text = i.key_text[1]
            else:
                if self.parent.current_lang == 'RU':
                    for i in self.parent.children:
                        i.text = i.key_text[2]
                if self.parent.current_lang == 'EN':
                    for i in self.parent.children:
                        i.text = i.key_text[0]


