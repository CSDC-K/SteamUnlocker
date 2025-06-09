# OPEN SOURCE VERSION
# 1.6
# MADE BY VV

# -> This version is with out license reg and auto update system.

import customtkinter
import tkinter as tk
import requests
import threading
import subprocess
import os
import zipfile
import shutil
import time
import sys
import socket
import json
import distutils.dir_util 

from tkinter import filedialog
from customtkinter import *


licUp = True
HID_DLL_PATH = os.path.join(sys._MEIPASS if hasattr(sys, '_MEIPASS') else '.', 'Sources', 'hid.dll')
DATA_FILE = os.path.join("Sources", 'data.json')
FIX_JSON_PATH = os.path.join("Sources", 'fix.json')


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")


def fade_in(win):
    for alpha in range(0, 101, 5):
        win.attributes("-alpha", alpha / 100)
        win.update()
        time.sleep(0.01)


def center_window(win, width, height):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")





def simple_messagebox(title, message, ask_yes_no=False):
    result = None
    win = CTkToplevel()
    win.title(title)
    win.geometry("300x160")
    win.resizable(False, False)
    center_window(win, 300, 160)
    label = CTkLabel(win, text=message, wraplength=280)
    label.pack(pady=20)
    if ask_yes_no:
        button_frame = CTkFrame(win)
        button_frame.pack(pady=10)

        def yes():
            nonlocal result
            result = True
            win.destroy()

        def no():
            nonlocal result
            result = False
            win.destroy()

        CTkButton(button_frame, text="Yes", command=yes, width=80).pack(side="left", padx=10)
        CTkButton(button_frame, text="No", command=no, width=80).pack(side="right", padx=10)
    else:
        CTkButton(win, text="OK", command=win.destroy, width=80).pack(pady=10)
    win.grab_set()
    win.wait_window()
    return result


def open_loader(parent):
    loader_window = CTkToplevel(parent)
    loader_window.title("Loader")
    center_window(loader_window, 500, 500)
    loader_window.resizable(False, False)
    loader_window.grab_set()
    fade_in(loader_window)

    frame = customtkinter.CTkFrame(loader_window, border_color="#450aee", border_width=1)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    title = customtkinter.CTkLabel(frame, text="Script Loader", font=("Helvetica", 20))
    title.grid(row=0, column=0, columnspan=3, pady=(10, 5))

    listbox = tk.Listbox(frame, bg="#2a2a2a", fg="white", width=45, height=10)
    listbox.grid(row=1, column=0, columnspan=3, pady=(5, 5))

    subTitle = customtkinter.CTkLabel(frame, text="Made by VV", font=("helvetica", 10, "bold"),
                                      text_color="#E100FF")
    subTitle.place(x=25, y=450)

    log = tk.Text(frame, height=8, width=60, bg="#101010", fg="lime", font=("Consolas", 10))
    log.grid(row=3, column=0, columnspan=3, pady=(5, 5))
    log.insert(tk.END, ">> Steam Unlocker <<\n$~ Version : 1.6 BUILD ~$\n")

    def refresh_list():
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump({"SteamPath": ""}, f, indent=4)

        listbox.delete(0, tk.END)
        with open(DATA_FILE, "r") as f:
            apps = json.load(f)
        for app in apps.keys():
            if app != "SteamPath":
                listbox.insert(tk.END, app)

    refresh_list()

    def add_script():
        selectZip = filedialog.askopenfilename(title="Select ZIP File", filetypes=[("ZIP files", "*.zip")])
        if not selectZip:
            return
        appNameDialog = CTkInputDialog(text="App Name:", title="Enter Name", button_hover_color="#006600")
        appName = appNameDialog.get_input()
        if not appName:
            return

        with open(DATA_FILE, "r") as f:
            apps = json.load(f)

        steamPath = apps.get("SteamPath", "")
        if not steamPath:
            log.insert(tk.END, ">> ❌ Steam path not set!\n")
            return

        luaFolder = os.path.join(steamPath, "config", "stplug-in")
        manifestFolder = os.path.join(steamPath, "config", "depotcache")

        os.makedirs(luaFolder, exist_ok=True)
        os.makedirs(manifestFolder, exist_ok=True)

        try:
            with zipfile.ZipFile(selectZip, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if file.endswith('.lua'):
                        target_path = os.path.join(luaFolder, os.path.basename(file))
                        with zip_ref.open(file) as source, open(target_path, 'wb') as target:
                            target.write(source.read())
                    elif file.endswith('.manifest'):
                        target_path = os.path.join(manifestFolder, os.path.basename(file))
                        with zip_ref.open(file) as source, open(target_path, 'wb') as target:
                            target.write(source.read())

            if appName not in apps:
                apps[appName] = {
                    "LuaFolder": luaFolder,
                    "ManifestFolder": manifestFolder
                }
                with open(DATA_FILE, "w") as f:
                    json.dump(apps, f, indent=4)
                listbox.insert(tk.END, appName)

            log.insert(tk.END, f">> {appName} Added.\n")
            subprocess.run(
                ["taskkill", "/F", "/IM", "steam.exe"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False
            )
            subprocess.Popen(steamPath + r"/steam.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
                
        except Exception as e:
            log.insert(tk.END, f">> ❌ Error adding: {e}\n")

    def delete_script():
        selection = listbox.curselection()
        if not selection:
            log.insert(tk.END, ">> ❌ Select an app to delete.\n")
            return

        appName = listbox.get(selection)
        confirmed = simple_messagebox("Confirmation",
                                      f"Are you sure you want to delete '{appName}'?",
                                      ask_yes_no=True)
        if not confirmed:
            log.insert(tk.END, f">> Deletion of {appName} cancelled.\n")
            return

        with open(DATA_FILE, "r") as f:
            apps = json.load(f)

        if appName in apps:
            lua_path = apps[appName]["LuaFolder"]
            manifest_path = apps[appName]["ManifestFolder"]

            if os.path.exists(lua_path):
                for file in os.listdir(lua_path):
                    if file.endswith(".lua"):
                        try:
                            os.remove(os.path.join(lua_path, file))
                        except Exception as e:
                            log.insert(tk.END, f">> ❌ Failed to delete {file}: {e}\n")

            if os.path.exists(manifest_path):
                for file in os.listdir(manifest_path):
                    if file.endswith(".manifest"):
                        try:
                            os.remove(os.path.join(manifest_path, file))
                        except Exception as e:
                            log.insert(tk.END, f">> ❌ Failed to delete {file}: {e}\n")

            del apps[appName]
            with open(DATA_FILE, "w") as f:
                json.dump(apps, f, indent=4)
            listbox.delete(selection)

            log.insert(tk.END, f">> {appName} deleted.\n")

    def choose_path():
        path = filedialog.askdirectory(title="Select Steam Folder")
        if path:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/IM", "steam.exe"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=False
                )

                target_file = os.path.join(path, "hid.dll")
                if os.path.abspath(HID_DLL_PATH) != os.path.abspath(target_file):
                    shutil.copy(HID_DLL_PATH, target_file)
                    print(f"Copied hid.dll to {target_file}")
                else:
                    print(f"Skipping copy: {HID_DLL_PATH} and {target_file} are the same file.")
            except Exception as e:
                log.insert(tk.END, f">> ❌ Failed to: {e}\nClose steam and retry.")
                simple_messagebox("Error", f"Failed to:\n{e}\nClose steam and retry.")
                return

            with open(DATA_FILE, "r") as f:
                apps = json.load(f)
            apps["SteamPath"] = path
            with open(DATA_FILE, "w") as f:
                json.dump(apps, f, indent=4)
            log.insert(tk.END, f">> Steam path saved: {path}\n")
            simple_messagebox("Success", f"Steam path saved:\n{path}")


    CTkButton(frame, text="Add", fg_color="#6A09C5", hover_color="#61059E", command=add_script).grid(row=2, column=0, padx=10, pady=10)
    CTkButton(frame, text="Delete", fg_color="#6A09C5", hover_color="#61059E", command=delete_script).grid(row=2, column=1, padx=10, pady=10)
    CTkButton(frame, text="Steam Path", fg_color="#6A09C5", hover_color="#61059E", command=choose_path).grid(row=2, column=2, padx=10, pady=10)


def main():
    mainPage = CTk()
    mainPage.title("Steam Unlocker || Main Page")
    mainPage.geometry("400x500")

    def fixSteam():
        global licUp
        print(licUp)
        if licUp == True:
            fixPage = CTkToplevel(mainPage)
            fixPage.geometry("400x500")
            fixPage.title("SteamUnlocker || Fixer")
            fixPage.grab_set()
            fixPageFrame = CTkFrame(fixPage, width=300, height=400, border_width=1, border_color="#450aee")
            fixPageFrame.place(x=50, y=50)

            fixTitle = CTkLabel(master=fixPageFrame, text="Fixer", font=("Helvetica", 21), text_color="#FFFFFF")
            fixTitle.place(x=125,y=25)
            dropdown = customtkinter.CTkComboBox(
                master=fixPageFrame,
                values=["RDR2", "GTA5","GTA4"],
                width=200,
                height=35,
                fg_color="#2e2e2e",
                border_color="#450aee",
                border_width=2,
                button_color="#61059E",
                button_hover_color="#8000FF",
                dropdown_fg_color="#1f1f1f",
                dropdown_hover_color="#61059E",
                dropdown_text_color="white",
                font=("Arial", 14),
                corner_radius=10,
                state="readonly",
                justify="center"
            )
            dropdown.place(x=50,y=150)

            def fixGTA5():
                if os.path.exists(FIX_JSON_PATH):
                    with open(FIX_JSON_PATH, "r") as f:
                        fix_data = json.load(f)
                else:
                    fix_data = {}

                gta5_path = fix_data.get("GTA5")
                required_files = ["launc.dll", "bink2w64.dll", "orig_socialclub.dll", "socialclub.dll","PlayGTAV.exe"]

                if not gta5_path or not all(os.path.exists(os.path.join(gta5_path, f)) for f in required_files):
                    new_path = filedialog.askdirectory(title="Select GTA 5 Folder")
                    if not new_path:
                        simple_messagebox("Error", "No folder selected!")
                        return

                    for file_name in required_files:
                        src = os.path.join("Sources", "fixer", "GTA5", file_name)
                        dst = os.path.join(new_path, file_name)
                        try:
                            shutil.copy(src, dst)
                            print(f"Copied {file_name} to {dst}")
                        except Exception as e:
                            simple_messagebox("Error", f"Failed to copy {file_name}: {e}")
                            return
                    fix_data["GTA5"] = new_path
                    with open(FIX_JSON_PATH, "w") as f:
                        json.dump(fix_data, f, indent=4)
                    simple_messagebox("Success", "GTA5 fix applied and saved.")
                else:
                    simple_messagebox("Info", "GTA5 fix already applied, Please run PlayGTAV.exe on gta 5 path.")


            def fixGTA4():
                if os.path.exists(FIX_JSON_PATH):
                    with open(FIX_JSON_PATH, "r") as f:
                        fix_data = json.load(f)
                else:
                    fix_data = {}

                gta4_path = fix_data.get("GTA4")
                required_files = ["launc.dll", "binkw32.dll", "orig_socialclub.dll", "socialclub.dll", "PlayGTAIV.exe", "GTAIV.exe"]


                if not gta4_path or not all(os.path.exists(os.path.join(gta4_path, f)) for f in required_files):
                    new_path = filedialog.askdirectory(title="Select GTA4 Folder")
                    if not new_path:
                        simple_messagebox("Error", "No folder selected!")
                        return


                    for file_name in required_files:
                        src = os.path.join("Sources", "fixer", "GTA4", file_name)
                        dst = os.path.join(new_path, file_name)
                        try:
                            shutil.copy(src, dst)
                            print(f"Copied {file_name} to {dst}")
                        except Exception as e:
                            simple_messagebox("Error", f"Failed to copy {file_name}: {e}")
                            return

                    # Save path to fix.json
                    fix_data["GTA4"] = new_path
                    with open(FIX_JSON_PATH, "w") as f:
                        json.dump(fix_data, f, indent=4)
                    simple_messagebox("Success", "GTA4 fix applied and saved.")
                else:
                    simple_messagebox("Info", "GTA4 fix already applied, Please run PlayGTAIV.exe or GTAIV.exe on gta4 path.")


            def fixRDR2():
                if os.path.exists(FIX_JSON_PATH):
                    with open(FIX_JSON_PATH, "r") as f:
                        fix_data = json.load(f)
                else:
                    fix_data = {}

                rdr2_path = fix_data.get("RDR2")
                required_files = ["1911.dll", "bink2w64.dll", "Launcher.exe", "RDR2Launcher.exe"]


                if not rdr2_path or not all(os.path.exists(os.path.join(rdr2_path, f)) for f in required_files):
                    new_path = filedialog.askdirectory(title="Select RDR2 Folder")
                    if not new_path:
                        simple_messagebox("Error", "No folder selected!")
                        return


                    for file_name in required_files:
                        src = os.path.join("Sources", "fixer", "RDR2", file_name)
                        dst = os.path.join(new_path, file_name)
                        try:
                            shutil.copy(src, dst)
                            print(f"Copied {file_name} to {dst}")
                        except Exception as e:
                            simple_messagebox("Error", f"Failed to copy {file_name}: {e}")
                            return

                    # Save path to fix.json
                    fix_data["RDR2"] = new_path
                    with open(FIX_JSON_PATH, "w") as f:
                        json.dump(fix_data, f, indent=4)
                    simple_messagebox("Success", "RDR2 fix applied and saved.")
                else:
                    simple_messagebox("Info", "RDR2 fix already applied, Please run Launcher.exe on rdr2 path.")

            def runFix():
                game = dropdown.get()
                print(game)
                if game == "RDR2":
                    fixRDR2()
                elif game == "GTA5":
                    fixGTA5()
                elif game == "GTA4":
                    fixGTA4()

                else:
                    simple_messagebox("Error", "Please select a game.")

            fixButton = CTkButton(
                master=fixPageFrame,
                text="Fix",
                hover_color="#61059E",
                corner_radius=20,
                width=150,
                height=30,
                fg_color="#3e03b6",
                font=("Sans Serif", 20),
                command=runFix
            )
            fixButton.place(x=70,y=300)

        else:
            simple_messagebox("License Error", "Not Entered License!")


    def start_license_flow():
        global licUp
        print(licUp)
        if licUp == True:
            open_loader(mainPage)

    mainpageFrame = CTkFrame(master=mainPage, width=300, height=400, corner_radius=20, border_width=1,
                             border_color="#450aee", fg_color="#191919")
    mainTitle = CTkLabel(master=mainpageFrame, text="Steam Unlocker", font=("Helvetica", 21), text_color="#FFFFFF")
    subTitle = customtkinter.CTkLabel(mainpageFrame, text="Made by VV", font=("helvetica", 10, "bold"),
                                      text_color="#E100FF")
    itemPageButton = CTkButton(master=mainpageFrame, text="Start", hover_color="#61059E", corner_radius=20,
                               width=200, height=40, fg_color="#3e03b6",
                               font=("Sans Serif", 20), command=start_license_flow)
    
    fixPageButton = CTkButton(master=mainpageFrame, text="Fixer", hover_color="#61059E", corner_radius=20,
                               width=200, height=40, fg_color="#3e03b6",
                               font=("Sans Serif", 20), command=fixSteam)


    mainpageFrame.place(x=50, y=50)
    mainTitle.place(x=75, y=25)
    subTitle.place(x=25, y=360)
    itemPageButton.place(x=50, y=125)
    fixPageButton.place(x=50,y=200)

    mainPage.mainloop()


if __name__ == "__main__":
    main()
