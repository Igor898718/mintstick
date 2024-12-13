#!/usr/bin/python3
import urllib.request
import subprocess
import gi

gi.require_version('UDisks', '2.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, UDisks, GLib

class Installer():
    def __init__(self):
        self.wTree = Gtk.Builder()
        self.window = self.wTree.get_object("main_window")
        self.udisks_client = UDisks.Client.new_sync()
        self.selected_device = None

    def Download(self):
        # Загрузка архива Ventoy
        urllib.request.urlretrieve("https://github.com/ventoy/Ventoy/releases/download/v1.0.99/ventoy-1.0.99-linux.tar.gz", "ventoy-1.0.99-linux.tar.gz")
        # Извлечение архива Ventoy
        subprocess.run(["tar", "-xf", "ventoy-1.0.99-linux.tar.gz"])

    def get_available_devices(self):
        devices = {}
        manager = self.udisks_client.get_object_manager()
        for obj in manager.get_objects():
            if obj is not None:
                block = obj.get_block()
                if block is not None:
                    drive = self.udisks_client.get_drive_for_block(block)
                    if drive is not None:
                        device_id = drive.get_property('id')
                        
                        device_path = block.get_cached_property('device')
                        if device_path is not None:
                            device_path = device_path.get_by_id('unix-device')
                        
                        if device_path is None:
                            device_path = block.get_cached_property('device-file')
                        
                        devices[device_id] = device_path
        
        return devices
    def show_device_selection_dialog(self):
        dialog = Gtk.Dialog(title=("Select Device"), parent=self.window, flags=Gtk.DialogFlags.MODAL)
        dialog.add_buttons(("Cancel"), Gtk.ResponseType.CANCEL, ("OK"), Gtk.ResponseType.OK)

        available_devices = self.get_available_devices()
        list_store = Gtk.ListStore(str, str)
        
        for device_id, device_path in available_devices.items():
            list_store.append([device_id, device_path])

        tree_view = Gtk.TreeView(model=list_store)
        
    
        column = Gtk.TreeViewColumn("Device ID")
        cell_renderer = Gtk.CellRendererText()
        column.pack_start(cell_renderer, True)
        column.add_attribute(cell_renderer, "text", 0)

        tree_view.append_column(column)
        tree_view.set_headers_visible(True)  
        
        dialog.vbox.pack_start(tree_view, True, True, 0)
        dialog.vbox.show_all()

        result = dialog.run()
        if result == Gtk.ResponseType.OK:
            selection = tree_view.get_selection()
            model, selected_item = selection.get_selected()
            if selected_item:
                self.selected_device = model[selected_item][1]
                print(f"Выбранное устройство: {self.selected_device}")

        else:
            self.selected_device = None  # Если нажата кнопка Cancel или закрыто окно
        dialog.destroy()

    def get_selected_device(self):
        return self.selected_device

a = Installer()
a.show_device_selection_dialog()

if a.get_selected_device():
    print(f"Пользователь выбрал устройство: {a.get_selected_device()}")
else:
    print("Устройство не было выбрано")
