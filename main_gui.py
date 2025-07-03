import sys
import os
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QLabel, QCheckBox, QTabWidget, 
                             QHBoxLayout, QComboBox, QGridLayout)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QMainWindow):
    BASE_DIR = os.path.join(os.getcwd(), "pics_bg/")

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

        # Energy Controls
        self.energy_min_label = QLabel("Min Energy: 0")
        self.energy_max_label = QLabel("Max Energy: 10")

        self.energy_min_up = QPushButton("+")
        self.energy_min_down = QPushButton("-")
        self.energy_max_up = QPushButton("+")
        self.energy_max_down = QPushButton("-")

        self.energy_min_up.clicked.connect(self.increment_energy_min)
        self.energy_min_down.clicked.connect(self.decrement_energy_min)
        self.energy_max_up.clicked.connect(self.increment_energy_max)
        self.energy_max_down.clicked.connect(self.decrement_energy_max)

        energy_layout = QHBoxLayout()
        energy_layout.addWidget(self.energy_min_label)
        energy_layout.addWidget(self.energy_min_down)
        energy_layout.addWidget(self.energy_min_up)
        energy_layout.addWidget(self.energy_max_label)
        energy_layout.addWidget(self.energy_max_down)
        energy_layout.addWidget(self.energy_max_up)
        self.selection_layout.addLayout(energy_layout)

        # Vertex Controls
        self.vertex_min_label = QLabel("Min No. Tracks: 0")
        self.vertex_max_label = QLabel("Max No. Tracks: 5")

        self.vertex_min_up = QPushButton("+")
        self.vertex_min_down = QPushButton("-")
        self.vertex_max_up = QPushButton("+")
        self.vertex_max_down = QPushButton("-")

        self.vertex_min_up.clicked.connect(self.increment_vertex_min)
        self.vertex_min_down.clicked.connect(self.decrement_vertex_min)
        self.vertex_max_up.clicked.connect(self.increment_vertex_max)
        self.vertex_max_down.clicked.connect(self.decrement_vertex_max)

        vertex_layout = QHBoxLayout()
        vertex_layout.addWidget(self.vertex_min_label)
        vertex_layout.addWidget(self.vertex_min_down)
        vertex_layout.addWidget(self.vertex_min_up)
        vertex_layout.addWidget(self.vertex_max_label)
        vertex_layout.addWidget(self.vertex_max_down)
        vertex_layout.addWidget(self.vertex_max_up)
        self.selection_layout.addLayout(vertex_layout)

        # Real Events Tab Layout
        self.real_events_layout = QVBoxLayout(self.real_events_tab)
        self.show_events_button = QPushButton("Show Events")
        self.show_events_button.setStyleSheet("font-size: 50px;")
        self.show_events_button.setStyleSheet("color: black; background-color: orange;")
        self.show_events_button.clicked.connect(self.toggle_events_visibility)
        self.real_events_layout.addWidget(self.show_events_button)

        self.prev_button = QPushButton("Previous Event")
        self.prev_button.setStyleSheet("color: black; background-color: orange;")
        self.next_button = QPushButton("Next Event")
        self.next_button.setStyleSheet("color: black; background-color: orange;")
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
        conn = sqlite3.connect("sq_SN_database_bg_big.db")
        try:
            # Query to count the total number of tracks per event
            track_query = """
            SELECT event_number,
                COUNT(*) / 2 AS num_tracks
            FROM tracks
            GROUP BY event_number
            """
            self.df_tracks = pd.read_sql_query(track_query, conn)

            # Query to fetch calo_hits data
            calo_query = """
            SELECT event_number,
                energy,
                SUM(energy) OVER(PARTITION BY event_number) AS total_energy
            FROM calo_hits
            """
            self.df_calo = pd.read_sql_query(calo_query, conn)

            # Query to calculate time difference for events with more than 2 tracks
            time_diff_query = """
            SELECT event_number,
                MAX(calo_hit_time) - MIN(calo_hit_time) AS time_diff
            FROM calo_hits
            WHERE event_number IN (
                SELECT event_number
                FROM tracks
                GROUP BY event_number
                HAVING COUNT(*) / 2 > 2
            )
            GROUP BY event_number
            """
            self.df_time_diff = pd.read_sql_query(time_diff_query, conn)

            # Merge tracks and calo data to initialize self.df
            self.df = pd.merge(self.df_tracks, self.df_calo.drop(columns='energy'), on="event_number", how="outer")
            
        finally:
            conn.close()

    def increment_energy_min(self):
        min_energy = int(self.energy_min_label.text().split()[-1])
        min_energy += 1
        self.energy_min_label.setText(f"Min Energy: {min_energy}")
        self.update_plot_visibility()

    def decrement_energy_min(self):
        min_energy = int(self.energy_min_label.text().split()[-1])
        if min_energy > 0:
            min_energy -= 1
        self.energy_min_label.setText(f"Min Energy: {min_energy}")
        self.update_plot_visibility()

    def increment_energy_max(self):
        max_energy = int(self.energy_max_label.text().split()[-1])
        max_energy += 1
        self.energy_max_label.setText(f"Max Energy: {max_energy}")
        self.update_plot_visibility()

    def decrement_energy_max(self):
        max_energy = int(self.energy_max_label.text().split()[-1])
        if max_energy > 0:
            max_energy -= 1
        self.energy_max_label.setText(f"Max Energy: {max_energy}")
        self.update_plot_visibility()

    def increment_vertex_min(self):
        min_vertices = int(self.vertex_min_label.text().split()[-1])
        min_vertices += 1
        self.vertex_min_label.setText(f"Min No. Tracks: {min_vertices}")
        self.update_plot_visibility()

    def decrement_vertex_min(self):
        min_vertices = int(self.vertex_min_label.text().split()[-1])
        if min_vertices > 0:
            min_vertices -= 1
        self.vertex_min_label.setText(f"Min No. Tracks: {min_vertices}")
        self.update_plot_visibility()

    def increment_vertex_max(self):
        max_vertices = int(self.vertex_max_label.text().split()[-1])
        max_vertices += 1
        self.vertex_max_label.setText(f"Max No. Tracks: {max_vertices}")
        self.update_plot_visibility()

    def decrement_vertex_max(self):
        max_vertices = int(self.vertex_max_label.text().split()[-1])
        if max_vertices > 0:
            max_vertices -= 1
        self.vertex_max_label.setText(f"Max No. Tracks: {max_vertices}")
        self.update_plot_visibility()

    def update_plot_visibility(self):
        min_energy = int(self.energy_min_label.text().split()[-1])
        max_energy = int(self.energy_max_label.text().split()[-1])
        min_vertices = int(self.vertex_min_label.text().split()[-1])
        max_vertices = int(self.vertex_max_label.text().split()[-1])

        filtered_df = self.df[
            (self.df['total_energy'] >= min_energy) &
            (self.df['total_energy'] <= max_energy) &
            (self.df['num_tracks'] >= min_vertices * 2) &
            (self.df['num_tracks'] <= max_vertices * 2)
        ]

        self.valid_event_indices = filtered_df['event_number'].tolist()


        self.show_events_button.setVisible(True)
        self.prev_button.setVisible(False)
        self.next_button.setVisible(False)
        self.image_label.setVisible(False)
        self.event_number_label.setVisible(False)

        

        # Use the new button variables
        min_energy = int(self.energy_min_label.text().split()[-1])
        max_energy = int(self.energy_max_label.text().split()[-1])
        min_vertices = int(self.vertex_min_label.text().split()[-1])
        max_vertices = int(self.vertex_max_label.text().split()[-1])

        filtered_df = self.df[
            (self.df['total_energy'] >= min_energy) &
            (self.df['total_energy'] <= max_energy) &
            (self.df['num_tracks'] >= min_vertices * 2) &
            (self.df['num_tracks'] <= max_vertices * 2)
        ]

        filtered_calo_df = self.df_calo[
            self.df_calo['event_number'].isin(filtered_df['event_number'])
        ]

        filtered_time_diff = self.df_time_diff[
            self.df_time_diff['event_number'].isin(filtered_df['event_number'])
        ]

        self.valid_event_indices = filtered_df['event_number'].tolist()

        if self.total_energy_checkbox.isChecked():
            self.figure.clear()
            ax1 = self.figure.add_subplot(111)
            ax1.hist(filtered_df['total_energy'], bins=50, color='blue', alpha=0.7)
            ax1.set_title("Summed Energy per Event")
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
            ax2.set_title("Summed Energy per Activated OM")
            ax2.set_xlabel("Calo Energy")
            ax2.set_ylabel("Frequency")
            self.canvas_individual.draw()
            self.canvas_individual.setVisible(True)
        else:
            self.canvas_individual.setVisible(False)

        # New plot for time differences
        self.figure_calo_timing.clear()
        ax3 = self.figure_calo_timing.add_subplot(111)
        ax3.hist(filtered_time_diff['time_diff'], bins=50, color='orange', alpha=0.7)
        ax3.set_title("Time Difference Between First and Last Calo Hit")
        ax3.set_xlabel("Time Difference")
        ax3.set_ylabel("Frequency")
        self.canvas_calo_timing.draw()
        self.canvas_calo_timing.setVisible(True)

    def load_image(self):
        if self.valid_event_indices:
            try:
                event_number = self.valid_event_indices[self.event_index]
                image_path = os.path.join(self.BASE_DIR, f"1295_{int(event_number+1)}.png")
                if os.path.exists(image_path):
                    original_pixmap = QPixmap(image_path)
                    # Remove scaling to keep the original size, or adjust as needed
                    self.image_label.setPixmap(original_pixmap)
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
