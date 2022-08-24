from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.filemanager import MDFileManager
from kivymd.app import MDApp
from kivy.lang import Builder
import cv2
import numpy as np
import sqlite3
import os
app_path = os.path.dirname(os.path.abspath(__file__))
con = sqlite3.connect(os.path.join(app_path, 'demo.db'))
# KivyMd Widget

# Kivy Widget


class Application(ScreenManager):
    con = sqlite3.connect("apps.db")
    cor = con.cursor()
    cor.execute(
        "CREATE TABLE IF NOT EXISTS freshfish(id INTEGER PRIMARY KEY,image TEXT,status TEXT)")
    cor.execute(
        "CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    con.commit()
    data = {
        "Home": "home",
        "Data Save": "table",
        "Upload": "plus",
        "Clear": "delete",
        "Exit": "exit-to-app"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )

    def check(self):
        con = sqlite3.connect("apps.db")
        cor = con.cursor()
        images = self.ids.imgc.source
        img = cv2.imread(images)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width, _ = np.shape(img)
        data = np.reshape(img, (height * width, 3))
        data = np.float32(data)
        nc = 3
        criteria = (cv2.TERM_CRITERIA_EPS +
                    cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS
        comp, labels, centers = cv2.kmeans(
            data, nc, None, criteria, 10, flags)
        cv2.imwrite("gray.png", gray)
        self.ids.imgg.source = "gray.png"
        bars = []
        rgb_values = []
        font = cv2.FONT_HERSHEY_SIMPLEX

        for index, row in enumerate(centers):
            bar = np.zeros((200, 200, 3), np.uint8)
            bar[:] = row
            red, green, blue = int(row[2]), int(row[1]), int(row[0])
            result = (red+green+blue)//3
            print(result)
            bars.append(bar)
            rgb_values.append((red, green, blue))
        img_bar = np.hstack(bars)
        percent = []

        for index, row in enumerate(rgb_values):
            image = cv2.putText(
                img_bar, f'{index+1}.RGB: {row}', (5+200*index, 200-10), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
            percent.append(row[1])
            r = (sum(percent)/2295*100)
            print(r)
            print(f'{index+1}. RGB{row}')
            if r > 14.0:
                self.ids.resultc.text = "Ikan Segar"
                status = self.ids.resultc.text
            elif r <= 14.0:
                self.ids.resultc.text = "Ikan Tidak Segar"
                status = self.ids.resultc.text
        parameter = {
            'image': images,
            'status': status
        }
        cor.execute(
            "INSERT INTO freshfish(image,status) VALUES (:image, :status)", parameter)
        con.commit()
        con.close()

    def Regis(self):
        con = sqlite3.connect("apps.db")
        cor = con.cursor()
        x = cor.execute(
            "SELECT * FROM user WHERE username=?", (self.ids.user1.text,))
        if(x == ""):
            self.current = "regis"
        else:
            for a in x:
                usernm = a[1]
                passwd = a[2]
            if(self.ids.password1.text == self.ids.password2.text):
                parameter = {
                    'username': self.ids.user1.text,
                    'password': self.ids.password1.text
                }
                cor.execute(
                    "INSERT INTO user (username, password) VALUES (:username, :password)", parameter)
                con.commit()
                con.close()
                self.current = "Login"
            else:
                self.ids.msg.text = "Password Is Not Correct Please Insert Your Password Again"
                self.current = "regis"

    def Login(self):
        con = sqlite3.connect("apps.db")
        cor = con.cursor()
        cor.execute("SELECT * FROM user WHERE username=? & password=?",
                    (self.ids.user.text, self.ids.password.text,))
        print("Login Berhasil")
        self.current = "Home"

    def callback(self, instance):
        con = sqlite3.connect("apps.db")
        cor = con.cursor()
        if instance.icon == 'plus':
            self.file_manager_open()
        elif instance.icon == 'table':
            datas = cor.execute("SELECT * FROM freshfish")
            if datas == "":
                self.ids.view.add_widget(
                    MDLabel(text="Not Have Any Data Try", halign="center"))
            else:
                for data in datas:
                    self.ids.view.add_widget(
                        MDBoxLayout(
                            orientation='vertical',
                            name="alfa"
                        )
                    )
                    self.current.alfa.add_widget(MDLabel(
                        text=data[2]
                    ))
                    self.current.alfa.add_widget(Image(
                        source=data[1]
                    ))
            self.current = "tables"
        elif instance.icon == 'home':
            self.current = "Home"
        elif instance.icon == "delete":
            self.ids.imgc.source = ""
            self.ids.imgg.source = ""
            self.ids.resultc.text = "Result Check"
            self.current = "Home"
        else:
            self.current = "Login"

    def file_manager_open(self):
        self.file_manager.show('/')
        self.manager_open = True

    def select_path(self, path):
        self.ids.imgc.source = "C:"+path
        self.exit_manager()

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True


Builder.load_string("""
<Application>:
    Screen:
        name: "Login"
        MDCard:
            size_hint: None, None
            size: 300,400
            pos_hint: {'center_x': 0.5,'center_y': 0.5}
            elevation:10
            padding:25
            spacing:25
            orientation: 'vertical'
            MDLabel:
                id: welcome
                text: "Welcome"
                font_size:40
                halign: 'center'
                size_hint_y: None
                height: self.texture_size[1]
            MDTextFieldRound:
                id:user
                hint_text: "username"
                icon_right: "account"
                size_hint_x: None
                multiline:False
                width: 200
                font_size: 18
                pos_hint:{"center_x": 0.5}

            MDTextFieldRound:
                id:password
                hint_text: "password"
                icon_right: "eye-off"
                size_hint_x: None
                width: 200
                multiline:False
                font_size: 18
                pos_hint:{"center_x": 0.5}
                password: True

            MDRoundFlatButton:
                text: "LOG IN"
                font_size: 12
                pos_hint: {"center_x": 0.5}
                on_release: root.Login()
            MDRoundFlatButton:
                text: "Register"
                font_size: 12
                pos_hint: {"center_x": 0.5}
                on_release: root.current = 'regis'
            Widget:
                size_hint_y: None
                height: 10
    Screen:
        name: "regis"
        MDCard:
            size_hint: None, None
            size: 300,450
            pos_hint: {'center_x': 0.5,'center_y': 0.5}
            elevation:10
            padding:25
            spacing:25
            orientation: 'vertical'
            MDLabel:
                id: welcome
                text: "Register"
                font_size:40
                halign: 'center'
                size_hint_y: None
                height: self.texture_size[1]
            MDTextFieldRound:
                id:user1
                hint_text: "username"
                icon_right: "account"
                size_hint_x: None
                multiline:False
                width: 200
                font_size: 18
                pos_hint:{"center_x": 0.5}

            MDTextFieldRound:
                id:password1
                hint_text: "password"
                icon_right: "eye-off"
                size_hint_x: None
                width: 200
                multiline:False
                font_size: 18
                pos_hint:{"center_x": 0.5}
                password: True

            MDTextFieldRound:
                id:password2
                hint_text: "current password"
                icon_right: "eye-off"
                size_hint_x: None
                width: 200
                multiline:False
                font_size: 18
                pos_hint:{"center_x": 0.5}
                password: True

            MDRoundFlatButton:
                text: "Register"
                font_size: 12
                pos_hint: {"center_x": 0.5}
                on_release: root.Regis()
            MDRoundFlatButton:
                text: "LOG IN"
                font_size: 12
                pos_hint: {"center_x": 0.5}
                on_release: root.current = 'Login'
            Widget:
                size_hint_y: None
                height: 10

    Screen:
        name:"Home"
        MDCard:
            size_hint: None, None
            size: root.width, root.height
            pos_hint: {'center_x': 0.5,'center_y': 0.5}
            elevation:10
            padding:25
            spacing:25
            orientation: 'vertical'
            color: 255,255,255
            halign:"center"
            MDLabel:
                id: Halo
                text: "Kesegaran Ikan"
                font_size:40
                halign: 'center'
                size_hint_y: None
                height: self.texture_size[1]
                padding_y: 15
            Image:
                id: imgc
                size_hint_x:0.5
                pos_hint:{"center_x": 0.5}
            MDRoundFlatButton:
                text: "Check"
                font_size: 12
                pos_hint: {"center_x": 0.5}
                halign:'center'
                on_release:root.check()
            Image:
                id: imgg
                size_hint_x:0.5
                pos_hint:{"center_x": 0.5}
            MDLabel:
                id: resultc
                text: "Check Result"
                font_size:40
                halign: 'center'
                size_hint_y: None
                height: self.texture_size[1]
                padding_y: 15
            MDFloatingActionButtonSpeedDial:
                data: root.data
                root_button_anim: True
                callback: root.callback

    Screen:
        name: "tables"
        ScrollView:
            orientation: "vertical"
            MDGridLayout:
                cols: 2
                size_hint_y: 1
                id: view


        MDFloatingActionButtonSpeedDial:
            data: root.data
            root_button_anim: True
            callback: root.callback


""")


class FreshFishApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        return Application()


if __name__ == "__main__":
    FreshFishApp().run()
