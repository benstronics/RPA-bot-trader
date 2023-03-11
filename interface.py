import logging
import sys
import time
from datetime import datetime, timedelta
from dateutil.parser import parse
from functools import partial
import threading
from dataclasses import dataclass
import tkinter
#import customtkinter
from pathlib import Path
import copy
from tkcalendar import *
import customtkinter
import os
from PIL import Image, ImageTk
import pandas as pd


class Interface(customtkinter.CTk):
    """
        This class sets up a default interface to bots, specially those which are operate by colaborators
        suplying process options activities to be chosen by them.
        :param str color_theme = 'dark-blue'
    """
    def __init__(self,super_init:bool=True,color_theme:str="green",default_frame:str='home',appearance_mode:str="Dark",dimentions:str='800x700+0+0',title:str='Application'):
        self.color_theme = color_theme
        self.frame = default_frame
        self.appearance_mode = appearance_mode
        self.login_frame = None
        self.options_frame = None
        self.options_button = None
        self.status_change_color=False
        self.chrome_driver = False
        self.dimentions = dimentions
        self.table=None
        self.name_table=''
        self.titulo = title

        # define standard table dimention
        self.colunas_entry = None
        self.linhas_entry = None

        self.color_theme=self.criar_arquivo_cor_interface('color_theme','green')
        self.appearance_mode = self.criar_arquivo_cor_interface('appearance_mode', 'Dark')
        customtkinter.set_default_color_theme(self.color_theme)  # Themes: "blue" (standard), "green", "dark-blue"
        customtkinter.set_appearance_mode(self.appearance_mode)  # Modes: "System" (standard), "Dark", "Light"

        if super_init:
            super().__init__()

        self.title(self.titulo)
        self.geometry(self.dimentions)#800x800+100+100#+0+0

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        try:
            #image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
            image_path = f'{str(Path.cwd())}\images'
            #print(image_path)
            self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "logo.png")), size=(50, 50))
            self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "robot.png")), size=(30, 30))
            self.warning_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "warning.png")), size=(30, 30))
            self.info_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "info.png")), size=(30, 30))#
            self.calendar_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "calendar.png")), size=(30, 30))
            self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
            self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                         dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))
            self.options_image = customtkinter.CTkImage(
                light_image=Image.open(os.path.join(image_path, "options_dark.png")),
                dark_image=Image.open(os.path.join(image_path, "options_light.png")), size=(20, 20))
        except Exception as e:
            pass


        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)
        image = copy.copy(self.logo_image)
        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text=title, image=image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)
        image = copy.copy(self.home_image)
        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        image = copy.copy(self.add_user_image)
        self.config_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Configurações",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=image, anchor="w", command=self.config_button_event)
        self.config_button.grid(row=2, column=0, sticky="ew")

        # create config frame
        self.config_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.label_appearance_mode_menu = customtkinter.CTkLabel(self.config_frame, text="Background:", text_color=("gray10", "gray90"), font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_appearance_mode_menu.grid(row=0, column=0, padx=20, pady=10)

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self.config_frame, values=["Dark","Light"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=1, column=0, padx=20, pady=20, sticky="s")

        self.label_appearance_color_theme = customtkinter.CTkLabel(self.config_frame, text="Tema:", text_color=("gray10", "gray90"), font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_appearance_color_theme.grid(row=0, column=1, padx=20, pady=10)

        self.appearance_color_theme = customtkinter.CTkOptionMenu(self.config_frame,
                                                                values=["Blue", "Dark-blue", "Green"],
                                                                command=self.change_appearance_color_theme_event)
        self.appearance_color_theme.grid(row=1, column=1, padx=20, pady=20, sticky="s")

        self.create_menu_config_credentials_options()
        self.create_menu_config_filtros_options()

        # create home frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid(row=0, column=0, sticky="nsew")
        self.home_frame.grid_columnconfigure(0, weight=1)



        # select default frame
        self.select_frame_by_name(self.frame)

    def criar_arquivo_cor_interface(self,nome_arquivo:str,cor_padrao:str='',title:str='Escolha uma cor'):
        from referencias import Referencias
        cd = Referencias(gui=self)
        cd.verificar_ou_criar_pasta('filtros_config')
        registro = cd.criar_arquivo_json(['color_menu'], [cor_padrao], nome_arquivo)
        color = registro['color_menu']
        if self.status_change_color == True or len(color)<=0:
            registro = cd.criar_arquivo_json(['color_menu'], [str(cor_padrao)], nome_arquivo,
                                             substituir=True)
            color = registro['color_menu']
            self.status_change_color = False
        return color

    def on_closing(self):
        self.destroy()
        self.sair = True
        return self.sair


    def __copy__(self):
        return Interface(self)

    def loop(self):
        self.sair = False
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        if not self.sair:
            self.mainloop()
        self.__init__()

        #exit()


    def on_closing_top(self,master,window):
        try:
            window.quit()
        except:
            pass
        try:
            master.destroy()
        except:
            pass



    def loop_top(self,master,window):
        window.protocol("WM_DELETE_WINDOW", partial(self.on_closing_top,master,window))
        window.mainloop()

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")

        self.config_button.configure(fg_color=("gray75", "gray25") if name == "config" else "transparent")

        if self.options_button != None:
            self.options_button.configure(fg_color=("gray75", "gray25") if name == "config" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()

        if name == "config":
            self.config_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.config_frame.grid_forget()

        if name == "login":
            self.config_credentials_option(self.list_param_entry)
        else:
            if self.login_frame != None:
                self.login_frame.grid_forget()

        if name == "options":
            self.options_frame.grid(row=0, column=1, sticky="nsew")
        else:
            if self.options_frame != None:
                self.options_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def config_button_event(self):
        self.select_frame_by_name("config")

    def options_button_event(self):
        self.select_frame_by_name("options")

    def change_appearance_mode_event(self, new_appearance_mode):
        self.status_change_color=True
        self.appearance_mode = new_appearance_mode

        self.appearance_mode = self.criar_arquivo_cor_interface('appearance_mode', self.appearance_mode)
        customtkinter.set_appearance_mode(self.appearance_mode)

    def change_appearance_color_theme_event(self, new_appearance_theme):
        self.status_change_color=True
        #print(new_appearance_theme)
        new_appearance_theme =  new_appearance_theme.lower()
        self.appearance_color_theme = new_appearance_theme
        self.color_theme = self.criar_arquivo_cor_interface('color_theme', self.appearance_color_theme)
        customtkinter.set_default_color_theme(self.appearance_color_theme)
        self.destroy()
        #self.__init__(super_init=False,color_theme=self.appearance_color_theme,default_frame='config',appearance_mode=self.appearance_mode)


    def create_menu_config_credentials_options(self):
        def sets_up_credentials(option):
            if len(option)>0:
                from referencias import Referencias
                cd = Referencias(gui=self)
                credential = cd.importar_arquivo('PARAMETROS',option,'','')
                #print(credential)
                parametros_entry = list(credential.keys())
                #print(parametros_entry)
                len_prefix = len('Credenciais_')
                cuted_name_credential = str(option)[len_prefix:].split('.')[0]
                #print(cuted_name_credential)
                if 'chrome_driver' in cuted_name_credential.lower():
                    self.chrome_driver = True
                cd.delete_file('PARAMETROS',option)
                cd.criar_credenciais(cuted_name_credential,parametros_entry,destroy_gui=True)
        arquivos = Path('PARAMETROS/')

        arquivos = [''] + [str(arquivo.name) for arquivo in arquivos.iterdir() if 'credenciais' in str(arquivo.name).lower() and not 'postgre' in str(arquivo.name).lower()and not '.xlsx' in str(arquivo.name).lower()]
        #print(arquivos)

        self.label_config_credentials = customtkinter.CTkLabel(self.config_frame, text="Configurar Credenciais:",
                                                                   text_color=("gray10", "gray90"),
                                                                   font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_config_credentials.grid(row=2, column=0, padx=20, pady=10)

        self.credential_option = customtkinter.CTkOptionMenu(self.config_frame,
                                                                  values=arquivos,
                                                                  command=sets_up_credentials)
        self.credential_option.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")
        #self.mainloop()
    def create_menu_config_filtros_options(self):
        def sets_up_filtros(option):
            if len(option)>0:
                from referencias import Referencias
                cd = Referencias(gui=self)
                filtro = cd.importar_arquivo('filtros_config',option,'','')
                len_colunas = len(filtro.columns)
                len_linhas = len(filtro)
                self.create_table(colunas_entry=len_colunas,linhas_entry=len_linhas,nome_colunas=filtro.columns,lista_place_holds=filtro.values.tolist())
                pos=0
                df = pd.DataFrame()
                valores_colunas=[[] for _ in range(len_colunas)]
                for coluna in range(len_colunas):
                    for linhas in range(int(len(self.data_entry)/len_colunas)):
                        valores_colunas[coluna].append(self.data_entry[pos])
                        pos+=1
                    df[list(filtro.columns)[coluna]]=valores_colunas[coluna]
                #print(valores_colunas)
                #df=pd.DataFrame(valores_colunas)
                #df.columns = filtro.columns
                #print(df)
                cd.gerar_relatorio(df,option.split('.')[0],'filtros_config')

        arquivos = Path('filtros_config/')

        arquivos = [''] + [str(arquivo.name) for arquivo in arquivos.iterdir()]
        #print(arquivos)

        self.label_config_filtros = customtkinter.CTkLabel(self.config_frame, text="Configurar Filtros:",
                                                                   text_color=("gray10", "gray90"),
                                                                   font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_config_filtros.grid(row=4, column=0, padx=20, pady=10)

        self.filtro_option = customtkinter.CTkOptionMenu(self.config_frame,
                                                                  values=arquivos,
                                                                  command=sets_up_filtros)
        self.filtro_option.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")
        #self.mainloop()
    def create_menu_manange_files_folder(self,folder,frame:object, row:int=1, column:int=0):
        def sets_up_folder(option):
            if len(option)>0:
                from referencias import Referencias
                cd = Referencias(gui=self)
                filtro = cd.importar_arquivo(folder,option,'','')
                len_colunas = len(filtro.columns)
                len_linhas = len(filtro)
                self.create_table(colunas_entry=len_colunas,linhas_entry=len_linhas,nome_colunas=filtro.columns,lista_place_holds=filtro.values.tolist())
                pos=0
                df = pd.DataFrame()
                valores_colunas=[[] for _ in range(len_colunas)]
                for coluna in range(len_colunas):
                    for linhas in range(int(len(self.data_entry)/len_colunas)):
                        valores_colunas[coluna].append(self.data_entry[pos])
                        pos+=1
                    df[list(filtro.columns)[coluna]]=valores_colunas[coluna]
                #print(valores_colunas)
                #df=pd.DataFrame(valores_colunas)
                #df.columns = filtro.columns
                #print(df)
                self.table = df
                self.name_table = option
                extensao=option.split('.')[1]
                if 'xlsx' in extensao:
                    extensao ='excel'
                cd.gerar_relatorio(df,option.split('.')[0],folder,extensao)

        arquivos = Path(f'{folder}/')

        arquivos = [''] + [str(arquivo.name) for arquivo in arquivos.iterdir()]
        #print(arquivos)

        self.label_config_folder = customtkinter.CTkLabel(frame, text=f"Gerenciar arquivos {folder}:",
                                                                   text_color=("gray10", "gray90"),
                                                                   font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_config_folder.grid(row=row, column=column, padx=20, pady=10)

        self.folder_option = customtkinter.CTkOptionMenu(frame,
                                                                  values=arquivos,
                                                                  command=sets_up_folder)
        self.folder_option.grid(row=row+1, column=column, padx=20, pady=20, sticky="nsew")
        #self.mainloop()

    def config_credentials_option(self,list_param_entry,destroy:bool=True,top_level:bool=False,checkbox:bool=True):
        try:
            if top_level:
                master = customtkinter.CTk()
                window = customtkinter.CTkToplevel(master)
                window.geometry("400x700+100+100")
            else:
                master = self
                window = customtkinter.CTkToplevel(master)
            #self.window.geometry("355x700")
            window.attributes("-topmost", True)
            self.list_param_entry = list_param_entry
            #self.config_frame.grid_forget()
            # create login frame
            self.login_frame = customtkinter.CTkFrame(window)
            self.login_frame.grid_rowconfigure(0, weight=1)
            self.login_frame.grid_columnconfigure(0, weight=1)
            self.login_frame.grid(row=0, column=0, sticky="nsew")
            self.login_label = customtkinter.CTkLabel(self.login_frame, text="Insira suas credenciais abaixo\n",
                                                      font=customtkinter.CTkFont(size=20, weight="bold"))
            self.login_label.grid(row=0, column=0, padx=30, pady=(15, 15))
            self.param_entry=self.list_param_entry
            for row, param in enumerate(self.list_param_entry):
                if 'senha' in param.lower() or 'password' in param.lower():
                    self.param_entry[row] = customtkinter.CTkEntry(self.login_frame, width=200, show="*",
                                                                 placeholder_text=param)
                    self.param_entry[row].grid(row=row+1, column=0, padx=30, pady=(15, 15))
                else:
                    self.param_entry[row] = customtkinter.CTkEntry(self.login_frame, width=200, placeholder_text=param)
                    self.param_entry[row].grid(row=row+1, column=0, padx=30, pady=(15, 15))


            self.login_button = customtkinter.CTkButton(self.login_frame, text="Avançar", command=partial(self.login_event,destroy,master,window), width=200)
            self.login_button.grid(row=len(self.list_param_entry)+1, column=0, padx=30, pady=(15, 15))
            if checkbox:
                self.checkbox_1 = customtkinter.CTkCheckBox(self.login_frame,text='Lembrar-Me')
                self.checkbox_1.grid(row=len(self.list_param_entry)+2, column=0, pady=(15, 15), padx=20)
            if top_level:
                self.loop_top(window,window)
            else:
                window.mainloop()

        except Exception as e:
            #print(e)
            #window.destroy()
            self.config_credentials_option(list_param_entry,destroy,True,checkbox)



    def login_event(self,destroy:bool=True,master:object=None,window:object=None):
        if window==None:
            window=self
        self.resp_params_entry=['' for param in self.param_entry]
        for i, param in enumerate(self.param_entry):
            self.resp_params_entry[i] = str(param.get())
            #print(f'{i}: {param.get()}')
        try:
            self.checkbox_1_remember_me = self.checkbox_1.get()
        except Exception as e:
            #print(e)
            self.checkbox_1_remember_me = '1'
        #print('Lembrar-me :',self.checkbox_1_remember_me)
        list_len_param = [len(resp) for resp in self.resp_params_entry]
        #print(list_len_param)
        list_param_empty = ['vazio' if valor<=0 else '' for valor in list_len_param]
        #print(list_param_empty)
        try:
            vazio = list_param_empty.index('vazio')
            n_vazio = False
        except Exception as e:
            #print(e)
            n_vazio = True
        if n_vazio:
            pass
            self.login_frame.grid_forget()  # remove login frame
            #self.select_frame_by_name('config')
        else:
            self.warning('Insira as credenciais corretamente!')
        if destroy:
            #app = copy.copy(self)
            self.on_closing_top(window,window)
            #window.destroy()
            #app.mainloop()

        else:
            #self.quit()
            self.on_closing_top(window, window)
            #window.destroy()
            #time.sleep(2)
            #self.__init__(super_init=False,color_theme=self.color_theme,default_frame=self.frame,appearance_mode=self.appearance_mode)
            #self.after(1000,self.create_menu_config_credentials_options)
            #return




    def create_menu_buttons(self,qtde_button:int=1,list_label_buttons:list=[],list_functions_button:list=[]):
        self.list_label_buttons = list_label_buttons
        self.list_functions_button = list_functions_button
        self.qtde_button = qtde_button
        self.home_frame_button = list(range(self.qtde_button))
        for row in range(self.qtde_button):
            text = f'Botão {row + 1}'
            if len(self.list_label_buttons) > 0:
                text = self.list_label_buttons[row]
            if len(self.list_functions_button) == self.qtde_button:
                function = self.list_functions_button[row]
            else:
                def function(pos):
                    print(f'Botão {pos} sem função atribuida!')
            image = copy.copy(self.image_icon_image)
            self.home_frame_button[row] = customtkinter.CTkButton(self.home_frame, text=text,corner_radius=10, height=40, border_spacing=10,
                                                                  image=image,
                                                                  command=partial(function, row + 1),font=customtkinter.CTkFont(size=15))
            self.home_frame_button[row].grid(row=(row + 2), column=0, padx=20, pady=10, sticky="nsew",)
        #self.home_frame.grid_rowconfigure(10, weight=1)
    def warning(self,msg:str='',len_break_line=15,master:object=None):
        try:
            if master==None:
                master = customtkinter.CTk()
                #master.geometry("400x300+100+100")
            #master = master
            window = customtkinter.CTkToplevel(master)
            window.geometry("400x300+300+300")
            window.title("Aviso!")
            window.attributes("-topmost", True)
            new_msg = msg
            if len(msg)>len_break_line:
                list_words = msg.split()
                len_w = 0
                list_new_msg = []
                for word in list_words:
                    len_w += len(word)
                    if len_w < len_break_line:
                        list_new_msg.append(word)
                    else:
                        len_w = 0
                        list_new_msg.append(f'\n{word}')
                new_msg = ' '.join(list_new_msg).capitalize()
            # create label on CTkToplevel window
            image = copy.copy(self.warning_image)
            label = customtkinter.CTkLabel(window, text="Aviso!",image=image,compound="left", font=customtkinter.CTkFont(size=30, weight="bold"))
            label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")


            msg = customtkinter.CTkLabel(window, text=new_msg, font=customtkinter.CTkFont(size=15, weight="bold"))
            msg.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
            window.grid_rowconfigure(1, weight=1)
            window.grid_columnconfigure(0, weight=1)
            if master == self:
                self.mainloop()
            else:
                self.loop_top(master,window)
        except Exception as e:
            #print(e)
            self.on_closing_top(master,window)
            self.warning(msg,len_break_line,master=self)

    def info(self,msg:str='',len_break_line=15,master:object=None):
        try:
            if master == None:
                master = customtkinter.CTk()

            window = customtkinter.CTkToplevel(master)
            window.geometry("400x300+300+300")
            window.title("Info!")
            window.attributes("-topmost", True)
            new_msg=''
            if len(msg)>len_break_line:
                list_words = msg.split()
                len_w = 0
                list_new_msg = []
                for word in list_words:
                    len_w += len(word)
                    if len_w < len_break_line:
                        list_new_msg.append(word)
                    else:
                        len_w = 0
                        list_new_msg.append(f'\n{word}')
                new_msg = ' '.join(list_new_msg).capitalize()
            # create label on CTkToplevel window
            image = copy.copy(self.info_image)
            label = customtkinter.CTkLabel(window, text="Info!",image=image,compound="left", font=customtkinter.CTkFont(size=30, weight="bold"))
            label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

            msg = customtkinter.CTkLabel(window, text=new_msg, font=customtkinter.CTkFont(size=15, weight="bold"))
            msg.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
            window.grid_rowconfigure(1, weight=1)
            window.grid_columnconfigure(0, weight=1)
            if master == self:
                self.loop_top(window, window)
            else:
                self.loop_top(master, window)

        except Exception as e:
            #print(e)
            self.on_closing_top(master, window)
            self.info(msg, len_break_line, master=self)

    def entry_data(self,msg:str='',len_break_line=15,master:object=None):
        try:
            if master == None:
                master = customtkinter.CTk()
            window = customtkinter.CTkToplevel(master)
            window.geometry("400x300+300+300")
            window.title("Informe!")

            if len(msg)>len_break_line:
                list_words = msg.split()
                len_w = 0
                list_new_msg = []
                for word in list_words:
                    len_w += len(word)
                    if len_w < len_break_line:
                        list_new_msg.append(word)
                    else:
                        len_w = 0
                        list_new_msg.append(f'\n{word}')
                new_msg = ' '.join(list_new_msg).capitalize()
            # create label on CTkToplevel window
            image = copy.copy(self.info_image)
            label = customtkinter.CTkLabel(window, text="Info!",image=image,compound="left", font=customtkinter.CTkFont(size=30, weight="bold"))
            label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

            msg = customtkinter.CTkLabel(window, text=new_msg, font=customtkinter.CTkFont(size=15, weight="bold"))
            msg.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

            entry = customtkinter.CTkEntry(window, width=200, placeholder_text='Digite o valor aqui!')
            entry.grid(row=2, column=0, padx=30, pady=(15, 15))

            button = customtkinter.CTkButton(window, text="Avançar",
                                                    command=partial(self.save_entry_data, entry,master,window), width=200)
            button.grid(row=3, column=0, padx=30, pady=(15, 15))

            #window.grid_rowconfigure(1, weight=1)
            window.grid_columnconfigure(0, weight=1)
            if master == self:
                self.mainloop()
            else:
                self.loop_top(master, window)

        except Exception as e:
            #print(e)
            self.on_closing_top(master, window)
            self.entry_data(msg, len_break_line, master=self)

    def save_entry_data(self,entrys:list=[],master:object=None, window:object=None,optional_function:object=None):

        self.data_entry = ['' for entry in entrys]
        for i, entry in enumerate(entrys):
            entry._placeholder_text_active=None #to take the values of placeholder changed and unchanged
            self.data_entry[i] = str(entry.get())
        print(self.data_entry)
        if optional_function != None:
            optional_function()
        self.on_closing_top(window, window)

        # from ClasseReferencias import Referencias
        # cd = Referencias()
        # cd.criar_filtros()

    def get_calendar(self,master:object=None,formato:str='6'):
        try:
            def data(master:object=None,window:object=None):
                datai = calendario_inicio.get()
                data_inicio.set(datai)
                dataf = calendario_fim.get()
                data_fim.set(dataf)
                print(f'Periodo Selecionado {data_inicio.get()} a {data_fim.get()}')
                self.on_closing_top(window, window)

            if master == None:
                master = customtkinter.CTk()


            window = customtkinter.CTkToplevel(master)
            window.geometry("400x300+300+300")
            window.title("Período!")

            # image_path = f'{str(Path.cwd())}\images'
            # calendar_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "calendar.png")),
            #                                         size=(30, 30))
            msg = customtkinter.CTkLabel(window, text='Definir Período', font=customtkinter.CTkFont(size=25, weight="bold"))
            msg.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

            #image1 = copy.copy(self.info_image)
            msg = customtkinter.CTkLabel(window, text='Inicio do período',
                                         font=customtkinter.CTkFont(size=15, weight="bold"))
            msg.grid(row=2, column=0, padx=10, pady=10, sticky='ns')

            data_inicio = customtkinter.StringVar()
            calendario_inicio = DateEntry(window, year=datetime.today().year, locale='pt_br',anchor="n",justify='center', height=30)
            calendario_inicio.grid(row=3 , column=0, padx=10, pady=10,
                                   sticky='ns')
            #image2 = copy.copy(self.calendar_image)
            msg = customtkinter.CTkLabel(window, text='Final do período',
                                         font=customtkinter.CTkFont(size=15, weight="bold"))
            msg.grid(row=4, column=0, padx=10, pady=10, sticky='ns')

            data_fim = customtkinter.StringVar()
            calendario_fim = DateEntry(window, year=datetime.today().year, locale='pt_br',anchor="n",justify='center',height=30)
            calendario_fim.grid(row=5, column=0, padx=10, pady=10, sticky='ns')

            button = customtkinter.CTkButton(window, text="Avançar",
                                                    command=partial(data,master,window), width=200)
            button.grid(row=6, column=0, padx=30, pady=(15, 15))

            #window.grid_rowconfigure(1, weight=1)
            window.grid_columnconfigure(0, weight=1)
            if master == self:
                self.mainloop()
            else:
                self.loop_top(master, window)

            lista_data_ini = str(data_inicio.get()).split('/')
            lista_data_fin = str(data_fim.get()).split('/')
            if formato == '6':
                data_inicio = f'{lista_data_ini[0]}{lista_data_ini[1]}{lista_data_ini[2][-2:]}'
                data_fim = f'{lista_data_fin[0]}{lista_data_fin[1]}{lista_data_fin[2][-2:]}'
            elif formato == '8a':
                data_inicio = f'{lista_data_ini[0]}{lista_data_ini[1]}{lista_data_ini[2]}'
                data_fim = f'{lista_data_fin[0]}{lista_data_fin[1]}{lista_data_fin[2]}'
            elif formato == '8b':
                data_inicio = f'{lista_data_ini[0]}/{lista_data_ini[1]}/{lista_data_ini[2][2:]}'
                data_fim = f'{lista_data_fin[0]}/{lista_data_fin[1]}/{lista_data_fin[2][2:]}'
            elif formato == '10':
                data_inicio = f'{lista_data_ini[0]}/{lista_data_ini[1]}/{lista_data_ini[2]}'
                data_fim = f'{lista_data_fin[0]}/{lista_data_fin[1]}/{lista_data_fin[2]}'
            print(data_inicio, data_fim)

            return data_inicio, data_fim
        except Exception as e:
            logging.exception(e)
            pass

    def begin_progress_bar(self,tamanho,row:int=0):
        width = self.winfo_width()
        self.tamanho_progress = tamanho
        self.progressbar_1 = customtkinter.CTkProgressBar(self.home_frame, width=width, mode="determinate",determinate_speed=tamanho)
        self.progressbar_1.grid(row=row, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.step_progress = 1 / self.tamanho_progress
        self.progressbar_1.set(self.step_progress)
    def next_progress_bar(self):
        self.step_progress += 1 / self.tamanho_progress
        self.progressbar_1.set(self.step_progress)
        self.update()
    def end_progress_bar(self):
        self.progressbar_1.destroy()
        #self.frame_barra.destroy()
    def ask_table_dimentions(self,master:object=None):
        try:
            def entry_data(entrys:list = [], master: object = None, window: object = None):
                data_entry = ['' for entry in entrys]
                for i, entry in enumerate(entrys):
                    print(entry.get())
                    data_entry[i] = str(entry.get())
                print(data_entry)
                linhas_entry = int(str(data_entry[0]).strip())
                colunas_entry = int(str(data_entry[1]).strip())
                self.on_closing_top(window, window)
                self.create_table(colunas_entry=colunas_entry,linhas_entry=linhas_entry)

                # window.grid_rowconfigure(1, weight=1)
                # window.grid_columnconfigure(0, weight=1)
                #self.on_closing_top(window, window)

            # create label on CTkToplevel window
            #if master == None:
            #master = customtkinter.CTk()

            window = customtkinter.CTkToplevel(self)
            window.geometry('+0+0')#("400x300+300+300")
            window.attributes("-topmost", True)
            window.title("Informe!")

            image = copy.copy(self.info_image)

            label = customtkinter.CTkLabel(window, text="Qtde Colunas", image=image, compound="left",
                                           font=customtkinter.CTkFont(size=30, weight="bold"))
            label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

            entry2 = customtkinter.CTkEntry(window, width=200, placeholder_text='Digite o valor aqui!')
            entry2.grid(row=1, column=0, padx=30, pady=(15, 15))

            label = customtkinter.CTkLabel(window, text="Qtde Linhas",image=image,compound="left", font=customtkinter.CTkFont(size=30, weight="bold"))
            label.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

            entry1 = customtkinter.CTkEntry(window, width=200, placeholder_text='Digite o valor aqui!')
            entry1.grid(row=3, column=0, padx=30, pady=(15, 15))


            button = customtkinter.CTkButton(window, text="Avançar",
                                                    command=partial(entry_data,[entry1,entry2],master,window), width=200)
            button.grid(row=4, column=0, padx=30, pady=(15, 15))

            window.grid_rowconfigure(1, weight=1)
            window.grid_columnconfigure(0, weight=1)

            if master == self:
                #self.loop_top(window, window)
                self.mainloop()
            else:
                self.loop_top(master, window)


        except Exception as e:
            logging.exception(e)
            #self.on_closing_top(master, window)
            #self.ask_table_dimentions(master=self)

    def create_table(self,master:object=None,colunas_entry:int=3,linhas_entry:int=3,nome_colunas:list=[],lista_place_holds:list=[]):
        try:
            if len(lista_place_holds)<=0:
                lista_place_holds = [['' for _ in range(colunas_entry)] for _ in range(linhas_entry)]

            if self.colunas_entry != None:
                colunas_entry = self.colunas_entry
                linhas_entry = self.linhas_entry

            if len(nome_colunas)< colunas_entry:
                nome_colunas = [f'Coluna {i+1}' for i in range(colunas_entry)]

            # create label on CTkToplevel window
            if master == None:
                master = customtkinter.CTk()

            window = customtkinter.CTkToplevel(master)
            if linhas_entry>10:
                window.geometry('600x800+0+0')#600x800
            else:
                window.geometry('+0+0')  # ("400x300+300+300")#('+0+0')
            window.attributes("-topmost", True)
            window.title("Informe!")

            window.grid_rowconfigure(0, weight=1)
            window.grid_columnconfigure(0, weight=1)

            frame = customtkinter.CTkFrame(window, corner_radius=0)
            frame.grid(row=0, column=0, sticky="nsew")

            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)

            w, h = frame.winfo_screenwidth(), frame.winfo_screenheight()
            #customtkinter.set_appearance_mode("Dark")
            canvas = customtkinter.CTkCanvas(frame,highlightthickness=0,bg=self._apply_appearance_mode('black'), scrollregion=f"0 0 {w * 2} {h * 2}")#, scrollregion=f"0 0 {w * 2} {h * 2}"
            canvas.grid(row=0, column=0, sticky='nsew')



            second_frame = customtkinter.CTkFrame(canvas)
            second_frame.grid_rowconfigure(0, weight=1)
            second_frame.grid_columnconfigure(0, weight=1)

            canvas.create_window((0, 0), window=second_frame, anchor="nw")

            #image = copy.copy(self.info_image)

            label = customtkinter.CTkLabel(second_frame, text="Tabela",
                                           font=customtkinter.CTkFont(size=30, weight="bold"))
            label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
            global celula, pos
            celula = ['' for _ in range(colunas_entry * linhas_entry)]
            pos = 0
            for k, col in enumerate(nome_colunas):
                label = customtkinter.CTkLabel(second_frame, text=col, font=customtkinter.CTkFont(size=15, weight="bold"))
                label.grid(row=1, column=k, padx=10, pady=10, sticky="ew")
            for coluna in range(colunas_entry):
                for linha in range(linhas_entry):
                    celula[pos] = customtkinter.CTkEntry(second_frame, width=100)#,placeholder_text=lista_place_holds[linha][coluna]
                    celula[pos].grid(row=linha+2, column=coluna, padx=15, pady=15)
                    celula[pos].insert(0,lista_place_holds[linha][coluna])
                    pos += 1

            button = customtkinter.CTkButton(second_frame, text="Avançar",
                                             command=partial(self.save_entry_data, celula, master, window), width=100)
            button.grid(row=0, column=1, padx=15, pady=15)

            def more_row(row,colunas_entry):
                global celula,pos
                celula.append('')
                #global colunas_entry
                for coluna in range(colunas_entry):
                    celula[pos] = customtkinter.CTkEntry(second_frame, width=100,
                                                         placeholder_text='')
                    celula[pos].grid(row=int((len(celula)/colunas_entry)) + 2, column=coluna, padx=15, pady=15)
                    pos += 1

            plus_row = customtkinter.CTkButton(second_frame, text="Adicionar linha",
                                             command=partial(more_row,1,colunas_entry), width=100)
            plus_row.grid(row=0, column=2, padx=15, pady=15)

            # second_frame.grid(row=0, column=0, sticky="nsew")
            canvas.grid_rowconfigure(linhas_entry, weight=1)
            canvas.grid_columnconfigure(colunas_entry, weight=1)

            v = customtkinter.CTkScrollbar(window, orientation='vertical', command=canvas.yview)
            v.grid(row=0, column=colunas_entry, sticky='ns')

            h = customtkinter.CTkScrollbar(window, orientation='horizontal', command=canvas.xview)
            h.grid(row=linhas_entry, column=0, sticky='ew')

            canvas.config(yscrollcommand=v.set)
            canvas.config(xscrollcommand=h.set)
            canvas.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox('all')))
            if master == self:
                self.loop_top(window, window)
                #self.mainloop()
            else:
                self.loop_top(master, window)

        except Exception as e:
            logging.exception(e)
            # self.on_closing_top(master, window)
            # self.create_table(self,colunas_entry,linhas_entry,nome_colunas)

    def makescroll(self, parent, thing):
        v = customtkinter.CTkScrollbar(parent, orientation='vertical',command=thing.yview)
        v.grid(row=0, column=1, sticky='ns')
        thing.config(yscrollcommand=v.set)
        h = customtkinter.CTkScrollbar(parent, orientation='horizontal',command=thing.xview)
        h.grid(row=1, column=0, sticky='ew')
        thing.config(xscrollcommand=h.set)
        thing.bind("<Configure>", lambda e: thing.config(scrollregion=thing.bbox('all')))

    def select_options(self,list_options:list=[],text:str='Opções',list_optional_function:list=[],orient:str='vertical',offset_row:int=1,offset_column:int=0):
        try:
            def options(radio:object, master: object = None, window: object = None):
                valor = radio.get()
                print(f'Valor selecionado: {valor}')
                self.on_closing_top(window, window)

            image = copy.copy(self.options_image)
            self.options_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                       border_spacing=10, text="Opções",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=image, anchor="w", command=self.options_button_event)
            self.options_button.grid(row=3, column=0, sticky="ew")

            self.options_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
            # self.options_frame.grid_rowconfigure(0, weight=1)
            # self.options_frame.grid_columnconfigure(0, weight=1)
            #self.options_frame.grid(row=0, column=0, sticky="nsew")
            label = customtkinter.CTkLabel(self.options_frame, text=text,
                                           font=customtkinter.CTkFont(size=30, weight="bold"))
            label.grid(row=offset_row+1, column=0, padx=10, pady=10, sticky="ew")
            var_opcao = customtkinter.IntVar(value=999)
            if orient == 'horizontal':
                for i, opcao in enumerate(list_options):
                    # Grid.rowconfigure(Frame(self.root), i, weight=1)
                    opcao = str(opcao)
                    opcao_btn = customtkinter.CTkRadioButton(self.options_frame, text=opcao, variable=var_opcao, value=i + 1,
                                            command=partial(options,var_opcao))
                    opcao_btn.grid(row=offset_row+2, column=0, padx=10, pady=10, sticky='nsew')

            elif orient == 'vertical':
                for i, opcao in enumerate(list_options):
                    #Grid.rowconfigure(Frame(self.root), i, weight=1)
                    opcao = str(opcao)
                    opcao_btn = customtkinter.CTkRadioButton(self.options_frame,text=opcao, variable=var_opcao, value=i+1,
                                                           command=partial(options,var_opcao))
                    opcao_btn.grid(row=offset_row+2 + i, column=0, padx=10, pady=10, sticky='nsew')
            else:
                contador = 0
                coluna = 0
                for i, opcao in enumerate(list_options):
                    contador += 1
                    if contador >= (offset_column):
                        linhas_grid += 1
                        contador = 1
                        coluna = 0

                    opcao = str(opcao)
                    opcao_btn = customtkinter.CTkRadioButton(self.options_frame, text=opcao, variable=var_opcao, value=i + 1,
                                            command=partial(options,var_opcao))
                    opcao_btn.grid(row=offset_row+2 + linhas_grid, column=0, padx=10, pady=10, sticky='nsew')

        except Exception as e:
            logging.exception(e)
            #self.on_closing_top(master, window)
            #self.ask_table_dimentions(master=self)]
    def select_parameters(self,list_options:list=[],text:str='Opções',list_optional_check_box_functions:list=[],orient:str='vertical',offset_row:int=1,offset_column:int=0, optional_button_function:object=None):
        try:
            check_box = ['' for _ in list_options]

            def options(check:object, master: object = None, window: object = None):
                valor = check_box[check].get()
                print(f'Valor selecionado: {valor}')
                self.on_closing_top(window, window)

            image = copy.copy(self.options_image)
            self.options_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                       border_spacing=10, text="Opções",
                                                       fg_color="transparent", text_color=("gray10", "gray90"),
                                                       hover_color=("gray70", "gray30"),
                                                       image=image, anchor="w", command=self.options_button_event)
            self.options_button.grid(row=3, column=0, sticky="ew")

            self.options_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

            label = customtkinter.CTkLabel(self.options_frame, text=text,
                                           font=customtkinter.CTkFont(size=30, weight="bold"))
            label.grid(row=offset_row+1, column=0, padx=10, pady=10, sticky="ew")

            if orient == 'horizontal':
                for i, opcao in enumerate(list_options):
                    # Grid.rowconfigure(Frame(self.root), i, weight=1)
                    opcao = str(opcao)
                    check_box[i] = customtkinter.CTkCheckBox(self.options_frame, text=opcao,
                                            command=partial(options,i))
                    check_box[i].grid(row=offset_row+2, column=0, padx=10, pady=10, sticky='nsew')

            elif orient == 'vertical':
                for i, opcao in enumerate(list_options):
                    #Grid.rowconfigure(Frame(self.root), i, weight=1)
                    opcao = str(opcao)
                    check_box[i] = customtkinter.CTkCheckBox(self.options_frame,text=opcao,
                                                           command=partial(options,i))
                    check_box[i].grid(row=offset_row+2 + i, column=0, padx=10, pady=10, sticky='nsew')
            else:
                contador = 0
                coluna = 0
                for i, opcao in enumerate(list_options):
                    contador += 1
                    if contador >= (offset_column):
                        linhas_grid += 1
                        contador = 1
                        coluna = 0

                    opcao = str(opcao)
                    check_box[i] = customtkinter.CTkCheckBox(self.options_frame, text=opcao,
                                            command=partial(options,i))
                    check_box[i].grid(row=offset_row+2 + linhas_grid, column=0, padx=10, pady=10, sticky='nsew')

            button = customtkinter.CTkButton(self.options_frame, text="Avançar",
                                                        command=partial(self.save_entry_data,check_box,None,None,optional_button_function),
                                                        width=200)
            button.grid(row=offset_row + len(list_options) + 2 , column=0, padx=30, pady=(15, 15))
        except Exception as e:
            logging.exception(e)
            #self.on_closing_top(master, window)
            #self.ask_table_dimentions(master=self)]
    def set_resume_labels(self, list_labels_name, list_values, frame,offset_row,label_title):
        label_name_object=['' for _ in list_labels_name]
        label_value_object = ['' for _ in list_values]

        image = copy.copy(self.info_image)
        label = customtkinter.CTkLabel(frame, text=label_title, image=image, compound="left",
                                       font=customtkinter.CTkFont(size=30, weight="bold"))
        label.grid(row=offset_row+1, column=0, padx=10, pady=10, sticky="ew")
        for i, label_name in enumerate(list_labels_name):
            text = f'{label_name} : {list_values[i]}'.capitalize()
            label_name_object[i] = customtkinter.CTkLabel(frame, text=text,
                                           font=customtkinter.CTkFont(size=20))
            label_name_object[i].grid(row=offset_row +2 + i, column=0, padx=10, pady=10, sticky="ew")

    def set_image_labels(self, folder_img, width,height, frame,offset_row,optional_func:object=None):
        global pos,image_path,play
        pos=0

        images = os.listdir(folder_img)
        if len(images)==0:
            image_path = f'{str(Path.cwd())}\images'
            images=['logo.png']
        else:
            image_path = f'{str(Path.cwd())}\{folder_img}'
        def next_image(stop_play:bool=False):
            global pos,image_path,play_img
            if stop_play:
                play_img = False
            pos+=1
            if pos>=len(images):
                pos=0
            img = images[pos]
            img_label = customtkinter.CTkImage(Image.open(os.path.join(image_path, img)), size=(width, height))
            image = copy.copy(img_label)
            label = customtkinter.CTkLabel(frame, text='', image=image, compound="center",
                                           )
            label.grid(row=offset_row + 1, column=0, padx=10, pady=10, sticky="nsew")
            # label.grid_rowconfigure(0, weight=1)
            # label.grid_columnconfigure(0, weight=1)
            if play_img:
                self.after(100,play)
        def play():
            global play_img
            #for i in range(len(images)):
            play_img=True
            self.after(100,next_image)

        global play_img
        play_img = False
        img = images[pos] if pos < len(images) else images[0]
        img_label = customtkinter.CTkImage(Image.open(os.path.join(image_path, img)), size=(width, height))
        image = copy.copy(img_label)
        label = customtkinter.CTkLabel(frame, text='', image=image, compound="center")
        label.grid(row=offset_row+1, column=0, padx=10, pady=10, sticky="nsew")
        # label.grid_rowconfigure(0, weight=1)
        # label.grid_columnconfigure(0, weight=1)

        button = customtkinter.CTkButton(frame, text="Avançar",
                                         command=partial(next_image,True),
                                         width=200)
        button.grid(row=offset_row + 2, column=0, padx=10, pady=10)

        button2 = customtkinter.CTkButton(frame, text="Play",
                                         command=play,
                                         width=200)
        button2.grid(row=offset_row + 3, column=0, padx=10, pady=10)

    def create_menu_lista(self,frame,lista_options,function_comand,offset_row:int=0,offset_column:int=0):
        def set_function(option):
            function_comand(option)
        menu = customtkinter.CTkOptionMenu(frame,
                                                             values=lista_options,
                                                             command=set_function)
        menu.grid(row=offset_row, column=offset_column, padx=10, pady=10, sticky="nsew")


    def ask_user(self,msg:str='Digite algo?',titulo:str='Informar'):
        dialog = customtkinter.CTkInputDialog(text=msg, title=titulo)
        resp = dialog.get_input()
        print("Resposta:", resp)
        return resp

if __name__ == "__main__":
    def func(*args):
        print('função definida!')
        app.begin_progress_bar(10,5)
        for i in range(10):
            app.next_progress_bar()
            time.sleep(1)
        app.end_progress_bar()
    app = Interface()
    app.create_menu_buttons(2,['Gerar relatorio','Tratar dados'],[func,func])
    app.mainloop()

