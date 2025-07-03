import sys
import os
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QLabel, QCheckBox, QTabWidget, 
                             QSlider, QHBoxLayout)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QMainWindow):
    BASE_DIR = "/Users/s2408030/Desktop/Teaching/GUI/pics/"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperNEMO Data Analysis Tool")
        self.setGeometry(100, 100, 1600, 1200)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.tabs = QTabWidget()
        self.image_tab = QWidget()
        self.tabs.addTab(self.image_tab, "Individual Events")

        self.plots_tab = QWidget()
        self.tabs.addTab(self.plots_tab, "Analysis Plots")



        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.tabs)

        # Image Tab with Plot
        self.image_layout = QVBoxLayout(self.image_tab)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_layout.addWidget(self.image_label)

        # Main figure
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.image_layout.addWidget(self.canvas)

        # Second figure for individual energies
        self.figure_individual = plt.figure()
        self.canvas_individual = FigureCanvas(self.figure_individual)
        self.image_layout.addWidget(self.canvas_individual)

        # Checkboxes for plot selection
        self.total_energy_checkbox = QCheckBox("Show Total Energy")
        self.total_energy_checkbox.setChecked(True)
        self.total_energy_checkbox.stateChanged.connect(self.update_plot_visibility)
        
        self.individual_energy_checkbox = QCheckBox("Show Individual Calo Energy")
        self.individual_energy_checkbox.setChecked(True)
        self.individual_energy_checkbox.stateChanged.connect(self.update_plot_visibility)
        
        self.image_layout.addWidget(self.total_energy_checkbox)
        self.image_layout.addWidget(self.individual_energy_checkbox)

        self.slider_layout = QVBoxLayout()

        # Checkbox for Sliders
        self.energy_slider_checkbox = QCheckBox("Show Energy Slider")
        self.energy_slider_checkbox.stateChanged.connect(self.update_slider_visibility)
        self.vertex_slider_checkbox = QCheckBox("Show Vertex Slider")
        self.vertex_slider_checkbox.stateChanged.connect(self.update_slider_visibility)

        self.image_layout.addWidget(self.energy_slider_checkbox)
        self.image_layout.addWidget(self.vertex_slider_checkbox)

        # Energy Slider
        energy_layout = QHBoxLayout()
        self.energy_min_label = QLabel("Min Energy: 0")
        self.energy_max_label = QLabel("Max Energy: 100")
        self.energy_slider_min = QSlider(Qt.Horizontal)
        self.energy_slider_min.setRange(0, 100)
        self.energy_slider_min.valueChanged.connect(self.update_energy_min_label)
        self.energy_slider_max = QSlider(Qt.Horizontal)
        self.energy_slider_max.setRange(0, 100)
        self.energy_slider_max.setValue(100)
        self.energy_slider_max.valueChanged.connect(self.update_energy_max_label)

        energy_layout.addWidget(self.energy_min_label)
        energy_layout.addWidget(self.energy_slider_min)
        energy_layout.addWidget(self.energy_max_label)
        energy_layout.addWidget(self.energy_slider_max)
        self.slider_layout.addLayout(energy_layout)

        # Vertex Slider
        vertex_layout = QHBoxLayout()
        self.vertex_min_label = QLabel("Min Vertices: 0")
        self.vertex_max_label = QLabel("Max Vertices: 20")
        self.vertex_slider_min = QSlider(Qt.Horizontal)
        self.vertex_slider_min.setRange(0, 20)
        self.vertex_slider_min.valueChanged.connect(self.update_vertex_min_label)
        self.vertex_slider_max = QSlider(Qt.Horizontal)
        self.vertex_slider_max.setRange(0, 20)
        self.vertex_slider_max.setValue(20)
        self.vertex_slider_max.valueChanged.connect(self.update_vertex_max_label)

        vertex_layout.addWidget(self.vertex_min_label)
        vertex_layout.addWidget(self.vertex_slider_min)
        vertex_layout.addWidget(self.vertex_max_label)
        vertex_layout.addWidget(self.vertex_slider_max)
        self.slider_layout.addLayout(vertex_layout)

        self.image_layout.addLayout(self.slider_layout)

        self.prev_button = QPushButton("Previous Event")
        self.next_button = QPushButton("Next Event")
        self.prev_button.clicked.connect(self.previous_event)
        self.next_button.clicked.connect(self.next_event)
        self.image_layout.addWidget(self.prev_button)
        self.image_layout.addWidget(self.next_button)

        # Initialize properties
        self.valid_event_indices = []
        self.event_index = 0

        self.load_data()
        self.update_plot_visibility()  # Set initial visibility
        self.update_slider_visibility()
        self.load_image()

    def load_data(self):
        conn = sqlite3.connect("sq_SN_database.db")
        
        # Query for total energy and vertices
        event_query = """
        SELECT events.event_number,
            SUM(calo_hits.energy) as total_energy,
            COUNT(tracks.vertex_position) as num_vertices
        FROM events
        LEFT JOIN calo_hits ON events.event_number = calo_hits.event_number
        LEFT JOIN tracks ON events.event_number = tracks.event_number
        GROUP BY events.event_number
        """
        self.df = pd.read_sql_query(event_query, conn)

        # Query for individual calo energies
        calo_query = """
        SELECT events.event_number, calo_hits.energy 
        FROM calo_hits
        JOIN events ON events.event_number = calo_hits.event_number
        """
        self.df_calo = pd.read_sql_query(calo_query, conn)

        conn.close()

    def update_energy_min_label(self):
        min_value = self.energy_slider_min.value()
        max_value = self.energy_slider_max.value()
        if min_value > max_value:
            self.energy_slider_max.setValue(min_value)
        self.energy_min_label.setText(f"Min Energy: {min_value}")
        self.update_plot_visibility()

    def update_energy_max_label(self):
        max_value = self.energy_slider_max.value()
        min_value = self.energy_slider_min.value()
        if max_value < min_value:
            self.energy_slider_min.setValue(max_value)
        self.energy_max_label.setText(f"Max Energy: {max_value}")
        self.update_plot_visibility()

    def update_vertex_min_label(self):
        self.vertex_min_label.setText(f"Min Vertices: {self.vertex_slider_min.value()}")
        self.update_plot_visibility()

    def update_vertex_max_label(self):
        self.vertex_max_label.setText(f"Max Vertices: {self.vertex_slider_max.value()}")
        self.update_plot_visibility()

    def update_slider_visibility(self):
        # Show or hide the energy sliders
        energy_visible = self.energy_slider_checkbox.isChecked()
        self.energy_min_label.setVisible(energy_visible)
        self.energy_slider_min.setVisible(energy_visible)
        self.energy_max_label.setVisible(energy_visible)
        self.energy_slider_max.setVisible(energy_visible)
        
        # Show or hide the vertex sliders
        vertex_visible = self.vertex_slider_checkbox.isChecked()
        self.vertex_min_label.setVisible(vertex_visible)
        self.vertex_slider_min.setVisible(vertex_visible)
        self.vertex_max_label.setVisible(vertex_visible)
        self.vertex_slider_max.setVisible(vertex_visible)

    def update_plot_visibility(self):
        min_energy = self.energy_slider_min.value() if self.energy_slider_checkbox.isChecked() else 0
        max_energy = self.energy_slider_max.value() if self.energy_slider_checkbox.isChecked() else 100
        min_vertices = self.vertex_slider_min.value() if self.vertex_slider_checkbox.isChecked() else 0
        max_vertices = self.vertex_slider_max.value() if self.vertex_slider_checkbox.isChecked() else 20
        
        filtered_df = self.df[
            (self.df['total_energy'] >= min_energy) &
            (self.df['total_energy'] <= max_energy) &
            (self.df['num_vertices'] >= min_vertices) &
            (self.df['num_vertices'] <= max_vertices)
        ]
        
        filtered_calo_df = self.df_calo[
            self.df_calo['event_number'].isin(filtered_df['event_number'])
        ]
        
        self.valid_event_indices = filtered_df['event_number'].tolist()
        
        # Plot the total energy histogram
        if self.total_energy_checkbox.isChecked():
            self.figure.clear()
            ax1 = self.figure.add_subplot(111)
            ax1.hist(filtered_df['total_energy'], bins=50, color='blue', alpha=0.7)
            ax1.set_title("Total Energy Histogram")
            ax1.set_xlabel("Total Energy")
            ax1.set_ylabel("Frequency")
            self.canvas.draw()
            self.canvas.setVisible(True)
        else:
            self.canvas.setVisible(False)

        # Plot the individual calo energy histogram
        if self.individual_energy_checkbox.isChecked():
            self.figure_individual.clear()
            ax2 = self.figure_individual.add_subplot(111)
            ax2.hist(filtered_calo_df['energy'], bins=50, color='green', alpha=0.7)
            ax2.set_title("Individual Calo Energy Histogram")
            ax2.set_xlabel("Calo Energy")
            ax2.set_ylabel("Frequency")
            self.canvas_individual.draw()
            self.canvas_individual.setVisible(True)
        else:
            self.canvas_individual.setVisible(False)

    def load_image(self):
        if self.valid_event_indices:
            try:
                event_number = self.valid_event_indices[self.event_index]
                image_path = os.path.join(self.BASE_DIR, f"1295_{event_number}.png")
                if os.path.exists(image_path):
                    pixmap = QPixmap(image_path).scaled(1000, 900, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(pixmap)
                else:
                    self.image_label.setText("Image not found")
            except Exception:
                self.image_label.setText("Image not found")
        else:
            self.image_label.setText("No valid images")

    def next_event(self):
        if self.valid_event_indices and self.event_index < len(self.valid_event_indices) - 1:
            self.event_index += 1
            self.load_image()

    def previous_event(self):
        if self.valid_event_indices and self.event_index > 0:
            self.event_index -= 1
            self.load_image()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
