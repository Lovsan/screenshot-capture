import sys
import os
import datetime
import threading
import requests
import shutil
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QTabWidget,
    QLabel, QScrollArea, QGridLayout, QMenu, QAction, QInputDialog,
    QMessageBox, QFileDialog, QHBoxLayout, QSpinBox, QPushButton, QFormLayout
)
from PyQt5.QtGui import QPixmap, QCursor, QFont
from PyQt5.QtCore import QTimer, Qt
from PIL import ImageGrab, Image
from pynput import keyboard
from plyer import notification

class FullImageWindow(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Full-Size Image")
        self.layout = QVBoxLayout()
        self.image_label = QLabel()
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap)
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)
        self.resize(pixmap.width(), pixmap.height())

class ScreenshotListener(QWidget):
    def __init__(self):
        super().__init__()
        self.screenshot_list = []
        self.thumbnail_width = 500  # Default thumbnail width
        self.thumbnail_height = 500  # Default thumbnail height
        self.imgur_client_id = 'YOUR_IMGUR_CLIENT_ID'  # Replace with your Imgur client ID
        self.history_file = 'data/screenshot_history.json'
        self.init_ui()
        self.load_screenshot_history()
        self.start_keyboard_listener()

    def init_ui(self):
        self.setWindowTitle('Screenshot Capture')
        self.resize(1280, 720)  # Set initial window size to 1280x720 pixels

        # Set up the main layout
        main_layout = QVBoxLayout()

        # Create a QTabWidget
        self.tabs = QTabWidget()

        # First tab: Log
        self.log_tab = QWidget()
        self.log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_layout.addWidget(self.log_text)
        self.log_tab.setLayout(self.log_layout)
        self.tabs.addTab(self.log_tab, "Log")

        # Second tab: Screenshots Grid View
        self.grid_tab = QWidget()
        self.grid_layout = QVBoxLayout()

        # Settings Layout
        settings_layout = QHBoxLayout()
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setValue(self.thumbnail_width)
        self.width_spinbox.setRange(50, 500)
        self.width_spinbox.valueChanged.connect(self.update_thumbnail_size)

        self.height_spinbox = QSpinBox()
        self.height_spinbox.setValue(self.thumbnail_height)
        self.height_spinbox.setRange(50, 500)
        self.height_spinbox.valueChanged.connect(self.update_thumbnail_size)

        settings_layout.addWidget(QLabel("Thumbnail Width:"))
        settings_layout.addWidget(self.width_spinbox)
        settings_layout.addWidget(QLabel("Thumbnail Height:"))
        settings_layout.addWidget(self.height_spinbox)

        self.grid_layout.addLayout(settings_layout)
        # Scroll Area to contain the grid of images
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        self.grid_widget.setLayout(self.grid)
        self.scroll_area.setWidget(self.grid_widget)

        self.grid_layout.addWidget(self.scroll_area)
        self.grid_tab.setLayout(self.grid_layout)
        self.tabs.addTab(self.grid_tab, "Screenshots")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        self.show()

    def log_message(self, message):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def add_screenshot_to_grid(self, filepath, add_to_list=True):
        # Load the image as a pixmap and create a clickable label
        pixmap = QPixmap(filepath).scaled(
            self.thumbnail_width, self.thumbnail_height,
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        thumbnail = QLabel()
        thumbnail.setPixmap(pixmap)
        thumbnail.setScaledContents(True)
        thumbnail.setFixedSize(self.thumbnail_width, self.thumbnail_height)

        # Create a label for filename and creation date
        file_info_label = QLabel()
        file_info_label.setAlignment(Qt.AlignCenter)
        file_info_label.setFont(QFont('Arial', 9))
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
        filename = os.path.basename(filepath)
        file_info_label.setText(f"{filename}\n{creation_time}")

        # Create a vertical layout to hold the thumbnail and info
        thumb_layout = QVBoxLayout()
        thumb_layout.addWidget(thumbnail)
        thumb_layout.addWidget(file_info_label)

        # Create a widget to hold the layout
        thumb_widget = QWidget()
        thumb_widget.setLayout(thumb_layout)

        # Store the index for identification
        if add_to_list:
            self.screenshot_list.append(filepath)
            index = len(self.screenshot_list) - 1
        else:
            index = self.screenshot_list.index(filepath)

        # commented out to prevent fullscreen image to open on leftclick.
        #thumbnail.mousePressEvent = lambda event, idx=index: self.open_full_image(idx)
        thumb_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        thumb_widget.customContextMenuRequested.connect(lambda pos, idx=index: self.show_thumbnail_context_menu(pos, idx))

        # Calculate the number of thumbnails per row based on screen width
        screen_width = QApplication.desktop().screenGeometry().width()
        images_per_row = max(1, screen_width // (self.thumbnail_width + 10))  # Adding spacing
        row = index // images_per_row
        col = index % images_per_row

        self.grid.addWidget(thumb_widget, row, col)

    def update_thumbnail_size(self):
        self.thumbnail_width = self.width_spinbox.value()
        self.thumbnail_height = self.height_spinbox.value()
        # Refresh the grid with new thumbnail sizes
        self.refresh_thumbnail_grid()

    def refresh_thumbnail_grid(self):
        # Clear the grid
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)
        # Re-add all thumbnails with updated sizes
        for idx, filepath in enumerate(self.screenshot_list):
            self.add_screenshot_to_grid(filepath, add_to_list=False)

    def show_thumbnail_context_menu(self, position, index):
        menu = QMenu()
        open_action = QAction('Open in Fullsize', self)
        edit_action = QAction('Edit Image', self)
        rename_action = QAction('Rename', self)
        delete_action = QAction('Delete', self)
        upload_action = QAction('Upload (Imgur)', self)
        info_action = QAction('File Info', self)

        open_action.triggered.connect(lambda: self.open_full_image(index))
        edit_action.triggered.connect(lambda: self.edit_image(index))
        rename_action.triggered.connect(lambda: self.rename_image(index))
        delete_action.triggered.connect(lambda: self.delete_image(index))
        upload_action.triggered.connect(lambda: self.upload_to_imgur(self.screenshot_list[index]))
        info_action.triggered.connect(lambda: self.show_file_info(index))

        menu.addAction(open_action)
        menu.addAction(edit_action)
        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addAction(upload_action)
        menu.addAction(info_action)

        menu.exec_(QCursor.pos())

    def open_full_image(self, index):
        filepath = self.screenshot_list[index]
        self.full_image_window = FullImageWindow(filepath)
        self.full_image_window.show()

    def edit_image(self, index):
        filepath = self.screenshot_list[index]
        # Open the image in the default system editor
        try:
            if sys.platform.startswith('darwin'):
                os.system(f'open "{filepath}"')
            elif os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                os.system(f'xdg-open "{filepath}"')
            else:
                QMessageBox.warning(self, 'Error', 'Unsupported OS for editing images.')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not open image editor: {e}')

    def rename_image(self, index):
        filepath = self.screenshot_list[index]
        directory, filename = os.path.split(filepath)
        new_name, ok = QInputDialog.getText(self, 'Rename Image', 'Enter new name:', text=filename)
        if ok and new_name:
            new_path = os.path.join(directory, new_name)
            try:
                os.rename(filepath, new_path)
                self.screenshot_list[index] = new_path
                self.log_message(f'Renamed {filepath} to {new_path}')
                self.refresh_thumbnail_grid()
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not rename file: {e}')

    def delete_image(self, index):
        filepath = self.screenshot_list[index]
        reply = QMessageBox.question(
            self, 'Delete Image', f'Are you sure you want to delete {filepath}?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(filepath)
                self.screenshot_list.pop(index)
                self.refresh_thumbnail_grid()
                self.log_message(f'Deleted {filepath}')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not delete file: {e}')

    def show_file_info(self, index):
        filepath = self.screenshot_list[index]
        try:
            file_info = os.stat(filepath)
            info_msg = (
                f'File: {filepath}\n'
                f'Size: {file_info.st_size} bytes\n'
                f'Created: {datetime.datetime.fromtimestamp(file_info.st_ctime)}\n'
                f'Modified: {datetime.datetime.fromtimestamp(file_info.st_mtime)}'
            )
            QMessageBox.information(self, 'File Info', info_msg)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not retrieve file info: {e}')

    def upload_to_imgur(self, filepath):
        headers = {"Authorization": f"Client-ID {self.imgur_client_id}"}
        url = "https://api.imgur.com/3/image"

        with open(filepath, 'rb') as image_file:
            image_data = image_file.read()
            response = requests.post(
                url,
                headers=headers,
                files={'image': image_data}
            )

        if response.status_code == 200:
            data = response.json()
            image_link = data['data']['link']
            notification.notify(
                title='Image Uploaded',
                message=f'Image uploaded to Imgur: {image_link}',
                app_icon=None,
                timeout=5
            )
            self.log_message(f"Image uploaded: {image_link}")
        else:
            notification.notify(
                title='Upload Failed',
                message='Failed to upload image to Imgur.',
                app_icon=None,
                timeout=5
            )
            self.log_message("Failed to upload image to Imgur.")

    def save_screenshot_from_clipboard(self):
        # Get image from clipboard
        img = ImageGrab.grabclipboard()
        if isinstance(img, Image.Image):
            # Define the screenshot folder
            # screenshot_folder = ('screenshots') if you want to store them in the scripts/screenshots folder
            screenshot_folder = os.path.expanduser('~/screenshots/')
            if not os.path.exists(screenshot_folder):
                os.makedirs(screenshot_folder)

            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f'screenshot_{timestamp}.png'
            filepath = os.path.join(screenshot_folder, filename)

            try:
                # Save image
                img.save(filepath, 'PNG')

                # Update GUI with info
                log_msg = f'Screenshot saved to {filepath}'
                self.log_message(log_msg)
                self.add_screenshot_to_grid(filepath)
                # Notification
                notification.notify(
                    title='Screenshot Saved',
                    message=f'Screenshot saved to {filepath}',
                    app_icon=None,
                    timeout=5
                )

            except Exception as e:
                # Handle exceptions
                notification.notify(
                    title='Error Saving Screenshot',
                    message=str(e),
                    app_icon=None,
                    timeout=5
                )
                log_msg = f'Error: {e}'
                self.log_message(log_msg)
        else:
            # No image in clipboard
            notification.notify(
                title='No Screenshot Found',
                message='No image found in clipboard.',
                app_icon=None,
                timeout=5
            )
            log_msg = 'No image found in clipboard.'
            self.log_message(log_msg)

    def on_press(self, key):
        try:
            if key == keyboard.Key.print_screen:
                # Schedule the screenshot saving on the main thread
                QTimer.singleShot(0, self.save_screenshot_from_clipboard)
        except AttributeError:
            pass

    def start_keyboard_listener(self):
        # Start the keyboard listener in a separate thread
        listener_thread = threading.Thread(target=self.keyboard_listener, daemon=True)
        listener_thread.start()

    def keyboard_listener(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def closeEvent(self, event):
        # Save the screenshot history
        self.save_screenshot_history()
        event.accept()

    def save_screenshot_history(self):
        # Save the list of screenshots to a JSON file
        with open(self.history_file, 'w') as f:
            json.dump(self.screenshot_list, f)

    def load_screenshot_history(self):
        # Load the list of screenshots from the JSON file
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.screenshot_list = json.load(f)
            # Add screenshots to the grid
            for filepath in self.screenshot_list:
                if os.path.exists(filepath):
                    self.add_screenshot_to_grid(filepath, add_to_list=False)
                else:
                    self.log_message(f'File not found: {filepath}')
        else:
            self.screenshot_list = []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScreenshotListener()
    sys.exit(app.exec_())
