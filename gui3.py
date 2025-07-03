import sys
import os
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QLabel, QCheckBox, QTabWidget, 
                             QSlider, QHBoxLayout, QComboBox, QGridLayout)
from PyQt5.QtGui import QPixmap, QFont
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

        self.main_layout = QVBoxLayout(self.central_widget)

        # Top Tabs
        self.upper_tab = QTabWidget()
        self.data_type = QWidget()
        self.upper_tab.addTab(self.data_type, "Data Type")
        self.main_layout.addWidget(self.upper_tab)

        self.top_tabs = QTabWidget()
        self.selection_tab = QWidget()
        self.top_tabs.addTab(self.selection_tab, "Selection Cuts")
        self.main_layout.addWidget(self.top_tabs)

        # Bottom Tabs
        self.bottom_tabs = QTabWidget()
        self.real_events_tab = QWidget()
        self.analysis_plots_standard_tab = QWidget()
        self.analysis_plots_advanced_tab = QWidget()
        self.bottom_tabs.addTab(self.real_events_tab, "Real Events")
        self.bottom_tabs.addTab(self.analysis_plots_standard_tab, "Analysis Plots")
        self.bottom_tabs.addTab(self.analysis_plots_advanced_tab, "Advanced")
        self.main_layout.addWidget(self.bottom_tabs)

        # Data Type Tab Layout
        self.data_type_layout = QVBoxLayout(self.data_type)
        self.data_type_dropdown = QComboBox()
        self.data_type_dropdown.addItems(["Background", "Bismuth Source", "Neutron Source"])
        self.data_type_dropdown.currentIndexChanged.connect(self.on_data_type_change)
        self.data_type_layout.addWidget(QLabel("Select Data Type:"))
        self.data_type_layout.addWidget(self.data_type_dropdown)

        # Selection Cuts Tab Layout
        self.selection_layout = QVBoxLayout(self.selection_tab)

        self.energy_slider_checkbox = QCheckBox("Show Energy Slider")
        self.energy_slider_checkbox.setChecked(True)
        self.energy_slider_checkbox.stateChanged.connect(self.update_slider_visibility)
        
        self.vertex_slider_checkbox = QCheckBox("Show Vertex Slider")
        self.vertex_slider_checkbox.setChecked(True)
        self.vertex_slider_checkbox.stateChanged.connect(self.update_slider_visibility)

        self.selection_layout.addWidget(self.energy_slider_checkbox)
        self.selection_layout.addWidget(self.vertex_slider_checkbox)

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
        self.selection_layout.addLayout(energy_layout)

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
        self.selection_layout.addLayout(vertex_layout)

        # Real Events Tab Layout
        self.real_events_layout = QVBoxLayout(self.real_events_tab)
        self.show_events_button = QPushButton("Show Events")
        self.show_events_button.clicked.connect(self.toggle_events_visibility)
        self.real_events_layout.addWidget(self.show_events_button)

        self.prev_button = QPushButton("Previous Event")
        self.next_button = QPushButton("Next Event")
        self.prev_button.clicked.connect(self.previous_event)
        self.next_button.clicked.connect(self.next_event)
        self.real_events_layout.addWidget(self.prev_button)
        self.real_events_layout.addWidget(self.next_button)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.real_events_layout.addWidget(self.image_label)

        self.event_number_label = QLabel()
        self.event_number_label.setAlignment(Qt.AlignCenter)
        self.real_events_layout.addWidget(self.event_number_label)

        # Hide event controls initially
        self.prev_button.setVisible(False)
        self.next_button.setVisible(False)
        self.image_label.setVisible(False)
        self.event_number_label.setVisible(False)

        # Analysis Plots Tab Layout
        # Use a VBox layout to add the checkboxes above the grid
        self.analysis_layout = QVBoxLayout(self.analysis_plots_standard_tab)

        # Horizontal layout for checkboxes
        checkbox_layout = QHBoxLayout()
        self.total_energy_checkbox = QCheckBox("Show Total Energy")
        self.total_energy_checkbox.setChecked(True)
        self.total_energy_checkbox.stateChanged.connect(self.update_plot_visibility)

        self.individual_energy_checkbox = QCheckBox("Show Individual Calo Energy")
        self.individual_energy_checkbox.setChecked(True)
        self.individual_energy_checkbox.stateChanged.connect(self.update_plot_visibility)

        checkbox_layout.addWidget(self.total_energy_checkbox)
        checkbox_layout.addWidget(self.individual_energy_checkbox)

        self.analysis_layout.addLayout(checkbox_layout)

        # Grid layout for plots
        plot_grid_layout = QGridLayout()
        self.figure = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.figure)
        plot_grid_layout.addWidget(self.canvas, 0, 0)

        self.figure_individual = plt.figure(figsize=(5, 5))
        self.canvas_individual = FigureCanvas(self.figure_individual)
        plot_grid_layout.addWidget(self.canvas_individual, 0, 1)

        self.figure_calo_timing = plt.figure(figsize=(5, 5))
        self.canvas_calo_timing = FigureCanvas(self.figure_calo_timing)
        plot_grid_layout.addWidget(self.canvas_calo_timing, 1, 0)

        self.figure_calo_timing2 = plt.figure(figsize=(5, 5))
        self.canvas_calo_timing2 = FigureCanvas(self.figure_calo_timing2)
        plot_grid_layout.addWidget(self.canvas_calo_timing2, 1, 1)

        self.analysis_layout.addLayout(plot_grid_layout)

        # Initialize properties
        self.valid_event_indices = []
        self.event_index = 0

        self.data_type.setObjectName("dataTypeTab")
        self.selection_tab.setObjectName("selectionTab")
        self.real_events_tab.setObjectName("realEventsTab")
        self.analysis_plots_standard_tab.setObjectName("analysis_plots_standard_tab")
        self.analysis_plots_advanced_tab.setObjectName("analysis_plots_advanced_tab")

        self.setStyleSheet("""
            QWidget#dataTypeTab {
                background-color: darkblue;
            }
            QWidget#selectionTab {
                background-color: darkgreen;
            }
            QWidget#realEventsTab {
                background-color: white;
            }
            QWidget#analysis_plots_standard_tab {
                background-color: purple;
            }
            QWidget#analysis_plots_advanced_tab {
                background-color: darkred;
            }

            QPushButton.red {
                background-color: red;
                color: black;
                border: 1px solid black;
                padding: 6px;
            }

            QTabBar::tab {
                background: #007ACC; /* Blue */
                color: black;
                padding: 10px;
            }
            QTabBar::tab:selected {
                background: #005999; /* Darker Blue */
                color: black;
            }
        """)

        self.load_data()
        self.update_plot_visibility()  # Set initial visibility
        self.update_slider_visibility()
        self.load_image()

    def toggle_events_visibility(self):
        self.prev_button.setVisible(True)
        self.next_button.setVisible(True)
        self.image_label.setVisible(True)
        self.event_number_label.setVisible(True)
        self.show_events_button.setVisible(False)

    def on_data_type_change(self):
        selected_option = self.data_type_dropdown.currentText()
        print(f"Selected data type: {selected_option}")
        self.show_events_button.setVisible(True)
        self.prev_button.setVisible(False)
        self.next_button.setVisible(False)
        self.image_label.setVisible(False)
        self.event_number_label.setVisible(False)

    def load_data(self):
        conn = sqlite3.connect("sq_SN_database.db")
        
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

        calo_query = """
        SELECT events.event_number, calo_hits.energy 
        FROM calo_hits
        JOIN events ON events.event_number = calo_hits.event_number
        """
        self.df_calo = pd.read_sql_query(calo_query, conn)

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
        energy_visible = self.energy_slider_checkbox.isChecked()
        self.energy_min_label.setVisible(energy_visible)
        self.energy_slider_min.setVisible(energy_visible)
        self.energy_max_label.setVisible(energy_visible)
        self.energy_slider_max.setVisible(energy_visible)
        
        vertex_visible = self.vertex_slider_checkbox.isChecked()
        self.vertex_min_label.setVisible(vertex_visible)
        self.vertex_slider_min.setVisible(vertex_visible)
        self.vertex_max_label.setVisible(vertex_visible)
        self.vertex_slider_max.setVisible(vertex_visible)

    def update_plot_visibility(self):
        self.show_events_button.setVisible(True)
        self.prev_button.setVisible(False)
        self.next_button.setVisible(False)
        self.image_label.setVisible(False)
        self.event_number_label.setVisible(False)

        min_energy = self.energy_slider_min.value()
        max_energy = self.energy_slider_max.value()
        min_vertices = self.vertex_slider_min.value()
        max_vertices = self.vertex_slider_max.value()

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
                    original_pixmap = QPixmap(image_path)
                    pixmap = original_pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(pixmap)
                else:
                    self.image_label.setText("Image not found")
                
                self.event_number_label.setText(f"Event Number: {event_number}")
                font = QFont()
                font.setPointSize(30)
                self.event_number_label.setFont(font)
                self.event_number_label.setStyleSheet("color: black;")


            except Exception:
                self.image_label.setText("Image not found")
                self.event_number_label.setText("")
        else:
            self.image_label.setText("No valid images")
            self.event_number_label.setText("")

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
