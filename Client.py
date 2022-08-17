import os
import socket
from tkinter import *
import tkinter.messagebox

root = Tk()
root.title('FileFox')
root.geometry("1125x590")

IP = "localhost"
PORT = 4450
ADDR = (IP, PORT)
SIZE = 1024  ## byte .. buffer size
FORMAT = "utf-8"
CLIENT_PATH = "client"

class TestingGui:
    def __init__(self, master):
        self.clientLabel = Label(master, text= "Client Working Directory")
        self.clientLabel.place(x=0, y=160)
        self.clientDir = Text(master, height= 25, width=60)
        clientFiles = os.listdir("client")
        for files in clientFiles:
            self.clientDir.insert(END, files.ljust(20," ") + "Bytes: " + str(os.path.getsize(os.path.join("client", files)))+ '\n')
        self.clientDir.configure(state="disabled")
        self.clientDir.place(x=0,y=180)

        self.serverLabel = Label(master, text="Server Working Directory")
        self.serverLabel.place(x=645,y=160)
        self.serverDir = Text(master, height=25, width=60)
        self.serverDir.configure(state="disabled")
        self.serverDir.place(x=645,y=180)

        self.isConnected = False
        self.connectionBox = Text(master, height=1, width=40)
        self.connectionButton = Button(master, text="Connect", command=self.Connect)
        self.connectionButton.place(x=125,y=0)
        self.connectionBox.place(x=0, y=30)

        self.downloadBox = Text(master, height=1, width=40)
        self.downloadButton = Button(master, text="Download", command=self.Download)
        self.downloadButton.place(x=530, y=0)
        self.downloadBox.place(x=400, y=30)

        self.uploadBox = Text(master, height=1, width=40)
        self.uploadButton = Button(master, text="Upload", command=self.Upload)
        self.uploadButton.place(x= 935, y=0)
        self.uploadBox.place(x=800, y=30)

        self.deleteBox = Text(master, height=1, width=40)
        self.deleteButton = Button(master, text="Delete", command=self.Delete)
        self.deleteButton.place(x=340, y=60)
        self.deleteBox.place(x=200, y=90)

        self.renameBox = Text(master, height=1, width=40)
        self.renameButton = Button(master, text="Rename", command=self.Rename)
        self.renameButton.place(x=735, y=60)
        self.renameBox.place(x=600,y=90)

        self.logoutButton = Button(master, text="Logout", command=self.Logout)
        self.logoutButton.place(x=537.5, y=120)

    def updateClient(self):
        self.clientDir.configure(state="normal")
        self.clientDir.delete('1.0', END)
        clientFiles = os.listdir("client")
        for files in clientFiles:
            self.clientDir.insert(END, files.ljust(20," ") + "Bytes: " + str(os.path.getsize(os.path.join("client", files)))+ '\n')
        self.clientDir.update()
        self.clientDir.configure(state="disabled")

    def updateServer(self):
        client.send("DIR".encode(FORMAT))
        list = client.recv(SIZE).decode(FORMAT)
        list = list.split("@")
        filenames = list[0].lstrip("[").rstrip("]")
        #filenames = filenames.lstrip("'").rstrip("'")
        filenames = filenames.split(",")
        filesizes = list[1].lstrip("[").rstrip("]")
        filesizes = filesizes.split(",")

        self.serverDir.configure(state="normal")
        self.serverDir.delete('1.0', END)
        for x in range(len(filenames)):
            self.serverDir.insert(END, filenames[x].lstrip(" '").rstrip(" '").ljust(20, " ") + "Bytes: " + filesizes[x].lstrip(" ") + '\n')
        self.serverDir.update()
        self.serverDir.configure(state="disabled")

    def Delete(self):
        data = self.deleteBox.get("1.0", 'end-1c')
        self.deleteBox.delete('1.0', END)
        file_name = data
        if self.isConnected is True:
            client.send("DELETE".encode(FORMAT))
            client.send(file_name.encode(FORMAT))
            data = client.recv(SIZE).decode(FORMAT)
            cmd, msg = data.split('@')
            if " does not exist" in msg:
                tkinter.messagebox.showinfo("Delete Failed", f"{msg}")
            else:
                tkinter.messagebox.showinfo("Delete Successful", f"{msg}")
            self.updateServer()
        else:
            tkinter.messagebox.showinfo("Delete Error", "Connect to the Server first")

    def Logout(self):
        if self.isConnected is True:
            client.send("LOGOUT".encode(FORMAT))
            tkinter.messagebox.showinfo("Logout Successful", "Connection disconnected")
            self.serverDir.configure(state="normal")
            self.serverDir.delete('1.0', END)
            self.serverDir.update()
            self.serverDir.configure(state="disabled")
            self.isConnected = False
        else:
            tkinter.messagebox.showinfo("Logout Error", "No Connection established")

    def Rename(self):
        data = self.renameBox.get("1.0", 'end-1c')
        self.renameBox.delete('1.0', END)
        if self.isConnected is True:
            try:
                src, rename = data.split(" ")
                client.send("RENAME".encode(FORMAT))
                client.send(f"{src}@{rename}".encode(FORMAT))
                data = client.recv(SIZE).decode(FORMAT)
                cmd, msg = data.split('@')
                if " does not exist" in msg:
                    tkinter.messagebox.showinfo("Rename Failed", f"{msg}")
                else:
                    tkinter.messagebox.showinfo("Rename Successful", f"{msg}")
                    self.updateServer()
            except:
                tkinter.messagebox.showinfo("Rename Error", "Not enough arguments need a source and destination")
        else:
            tkinter.messagebox.showinfo("Rename Error", "Connect to the Server first")

    def Upload(self):
        data = self.uploadBox.get("1.0", 'end-1c')
        self.uploadBox.delete('1.0', END)
        file_name = data
        if self.isConnected is True:
            files = os.listdir(CLIENT_PATH)
            if file_name not in files:
                tkinter.messagebox.showinfo("File Error", "Invalid file name")
            else:
                file_add = os.path.join(CLIENT_PATH, file_name)
                file_size = os.path.getsize(file_add)
                client.send("UPLOAD".encode(FORMAT))
                client.send(f"{file_add}@{file_size}".encode(FORMAT))

            # Opens file and handles closing
                with open(file_add, "rb") as file:
                    bytecount = 0
                    # Runs loop while the bytecount is less than the size of the file
                    while bytecount < file_size:
                        data = file.read(SIZE)
                        if not (data):
                            break
                        client.sendall(data)
                        bytecount += len(data)
                data = client.recv(SIZE).decode(FORMAT)
                cmd, msg = data.split("@")
                if cmd == "OK":
                    tkinter.messagebox.showinfo("Upload Successful", f"{msg}")

                self.updateServer()
        else:
            tkinter.messagebox.showinfo("Upload Error", "Connect to Server first")

    def Connect(self):
        data = self.connectionBox.get("1.0", 'end-1c')
        self.connectionBox.delete('1.0', END)
        global client
        if self.isConnected is False:
            try:
                data = data.split(" ")
                IP = data[0]
                PORT = int(data[1])
                ADDR = (IP, PORT)
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(ADDR)
                data = client.recv(SIZE).decode(FORMAT)
                cmd, msg = data.split("@")
                if cmd == "OK":
                    tkinter.messagebox.showinfo("Connection Successful", f"{msg}")
                elif cmd == "DISCONNECTED":
                    tkinter.messagebox.showinfo("Connection Error", f"{msg}")
                self.updateServer()
                self.isConnected = True
            except:
                tkinter.messagebox.showinfo("Connection Error", "Unable to Connect. Please verify server info. Address and Port")
        else:
            tkinter.messagebox.showinfo("Connection Error", "Logout before making new connections")

    def Download(self):
        data = self.downloadBox.get("1.0", 'end-1c')
        self.downloadBox.delete('1.0', END)
        file_name = str(data)
        if self.isConnected is True:
            client.send("DOWNLOAD".encode(FORMAT))
            client.send(file_name.encode(FORMAT))
            error_check = client.recv(SIZE).decode(FORMAT)
            if error_check == "EXISTS":
                file_size = client.recv(SIZE).decode(FORMAT)
                with open(os.path.join(CLIENT_PATH, file_name), "wb") as file:
                    bytecount = 0

                    # Runs loop while bytecount is less than file size
                    while bytecount < int(file_size):
                        if (int(file_size) - bytecount) < SIZE:
                            remaining = int(file_size) - bytecount
                            data = client.recv(remaining)
                        else:
                            data = client.recv(SIZE)
                        if not (data):
                            break
                        file.write(data)
                        bytecount += len(data)
                data = client.recv(SIZE).decode(FORMAT)
                cmd, msg = data.split("@")
                if cmd == "OK":
                    tkinter.messagebox.showinfo("Download Successful", f"{msg}")
                self.updateClient()
            else:
                clear_error = client.recv(SIZE).decode(FORMAT)
                tkinter.messagebox.showinfo("Filename Error", file_name + " does not exist")
        else:
            tkinter.messagebox.showinfo("Download Error", "Connect to server first")


def main():
    gui = TestingGui(root)
    root.mainloop()

if __name__ == '__main__':
    main()
