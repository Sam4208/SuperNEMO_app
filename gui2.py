import sys
import os
import random
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTabWidget, QCheckBox, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk

class MainWindow(QMainWindow):
 

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 1600, 1200)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.tabs = QTabWidget()
        self.image_tab = QWidget()
        self.vtk_tab = QWidget()
        self.tabs.addTab(self.image_tab, "Images")
        self.tabs.addTab(self.vtk_tab, "3D Viewer")

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.tabs)


        # VTK Tab
        self.vtk_layout = QVBoxLayout(self.vtk_tab)
        self.vtkWidget = QVTKRenderWindowInteractor(self.vtk_tab)
        self.vtk_layout.addWidget(self.vtkWidget)

        self.cuboid_vis = QCheckBox("Yellow Cuboid")
        self.cylinders_vis = QCheckBox("Cylinders")
        self.floor_vis = QCheckBox("Floor")
        self.cuboid_vis.setChecked(True)
        self.cylinders_vis.setChecked(True)
        self.floor_vis.setChecked(True)

        self.vtk_layout.addWidget(self.cuboid_vis)
        self.vtk_layout.addWidget(self.cylinders_vis)
        self.vtk_layout.addWidget(self.floor_vis)

        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()

        self.line_pos = 0.0
        self.animation_started = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.red_line_actors = []
        self.cylinder_actors = []  # Store cylinder actors
        self.circle_actors = []
        self.generate_random_origin_and_directions()
        self.add_objects()

        self.cuboid_vis.stateChanged.connect(self.update_scene)
        self.cylinders_vis.stateChanged.connect(self.update_scene)
        self.floor_vis.stateChanged.connect(self.update_scene)
        self.iren.AddObserver("KeyPressEvent", self.on_key_event)


    

    def add_objects(self):
        self.renderer.SetBackground(1, 1, 1)  # White background
        self.renderer.RemoveAllViewProps()

        # Constants for dimensions
        yellow_width = 0.02
        yellow_length = 1.0
        yellow_height = 2.5
        end_cuboid_width = 0.1
        end_cuboid_length = 1.0
        end_cuboid_height = 2.5
        cylinder_radius = 0.01
        cylinder_height = 1.0
        floor_height = -0.55

        # Add main objects using constants
        if self.cuboid_vis.isChecked():
            self.create_cuboid(
                [-yellow_width / 2, -yellow_length / 2, -yellow_height / 2],
                [yellow_width / 2, yellow_length / 2, yellow_height / 2],
                (1, 1, 0)
            )

        if self.cylinders_vis.isChecked():
            if not self.cylinder_actors:  # Only place cylinders if they haven't been added
                self.place_cylinders(cylinder_radius, cylinder_height, yellow_width, end_cuboid_width, yellow_length)

        if self.floor_vis.isChecked():
            self.create_cuboid(
                [-1, floor_height, -1],
                [1, floor_height, 1],
                (0.5, 0.5, 0.5),
                0.3
            )

        # Add large rectangles at each end
        self.create_cuboid(
            [-yellow_length / 2 - end_cuboid_width, -end_cuboid_length / 2, -end_cuboid_height / 2],
            [-yellow_length / 2, end_cuboid_length / 2, end_cuboid_height / 2],
            (0, 0.5, 0.5)
        )
        self.create_cuboid(
            [yellow_length / 2, -end_cuboid_length / 2, -end_cuboid_height / 2],
            [yellow_length / 2 + end_cuboid_width, end_cuboid_length / 2, end_cuboid_height / 2],
            (0.5, 0, 0.5)
        )

        for actor in self.red_line_actors + self.cylinder_actors + self.circle_actors:
            self.renderer.AddActor(actor)

        self.vtkWidget.GetRenderWindow().Render()

    def place_cylinders(self, radius, height, yellow_width, end_cuboid_width, length):
        num_cylinders_each_side = 100
        num_columns = 10
        num_rows = num_cylinders_each_side // num_columns

        # Adjust position to avoid overlap, cylinders strictly between cuboids
        gap_between_cuboids = 0.1
        x_offset_outer = length / 2 + gap_between_cuboids / 2
        x_offset_inner = length / 2 + radius

        column_spacing = (gap_between_cuboids - x_offset_inner * 2) / (num_columns - 1)
        row_spacing = length / num_rows

        for side in [-1, 1]:
            x_positions = [side * (x_offset_inner + i * column_spacing) for i in range(num_columns)]
            z_positions = [-length / 2 + (row_spacing * i) for i in range(num_rows)]
            
            for x in x_positions:
                for z in z_positions:
                    self.add_cylinder(x, 0, z, height, radius)

    def add_cylinder(self, x, y, z, height, radius):
        cylinder_source = vtk.vtkCylinderSource()
        cylinder_source.SetCenter(x, y, z)
        cylinder_source.SetRadius(radius)
        cylinder_source.SetHeight(height)
        cylinder_source.SetResolution(15)

        cylinder_mapper = vtk.vtkPolyDataMapper()
        cylinder_mapper.SetInputConnection(cylinder_source.GetOutputPort())

        cylinder_actor = vtk.vtkActor()
        cylinder_actor.SetMapper(cylinder_mapper)
        cylinder_actor.GetProperty().SetColor(0, 1, 0)  # Green
        cylinder_actor.GetProperty().SetOpacity(0.3)  # Slightly transparent

        self.cylinder_actors.append(cylinder_actor)








    def create_cuboid(self, min_point, max_point, color, alpha=1.0):
        cube_source = vtk.vtkCubeSource()
        cube_source.SetBounds(min_point[0], max_point[0], min_point[1], max_point[1], min_point[2], max_point[2])

        cube_mapper = vtk.vtkPolyDataMapper()
        cube_mapper.SetInputConnection(cube_source.GetOutputPort())

        cube_actor = vtk.vtkActor()
        cube_actor.SetMapper(cube_mapper)
        cube_actor.GetProperty().SetColor(*color)
        cube_actor.GetProperty().SetOpacity(alpha)

        self.renderer.AddActor(cube_actor)


    def on_key_event(self, obj, event):
        key = self.iren.GetKeySym()
        if key == '1' and not self.animation_started:
            self.animation_started = True
            self.line_pos = 0.0
            self.red_line_actors.clear()
            self.circle_actors.clear()
            self.timer.start(20)  # Faster animation speed
        elif key == '3':
            self.reset_scene()

    def generate_random_origin_and_directions(self):
        # Generate random origin within the yellow cuboid dimensions
        self.origin = [
            random.uniform(-0.01, 0.01),  # Half of yellow_width
            random.uniform(-0.5, 0.5),    # Half of yellow_length
            random.uniform(-0.5, 0.5)     # Half of yellow_height
        ]
        self.direction1 = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]
        self.direction2 = [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)]

 

    def update_animation(self):
        self.line_pos += 0.05  # Faster motion
        if self.line_pos > 1.0:
            self.line_pos = 1.0
            self.animation_started = False
            self.timer.stop()
        self.add_objects()
        self.add_animated_lines_and_circles()

    def add_animated_lines_and_circles(self):
        line_source1 = vtk.vtkLineSource()
        line_source1.SetPoint1(self.origin)
        line_source1.SetPoint2(
            self.origin[0] + self.line_pos * self.direction1[0],
            self.origin[1] + self.line_pos * self.direction1[1],
            self.origin[2] + self.line_pos * self.direction1[2],
        )
        line_mapper1 = vtk.vtkPolyDataMapper()
        line_mapper1.SetInputConnection(line_source1.GetOutputPort())

        line_actor1 = vtk.vtkActor()
        line_actor1.SetMapper(line_mapper1)
        line_actor1.GetProperty().SetColor(1, 0, 0)  # Red
        line_actor1.GetProperty().SetLineWidth(2)

        line_source2 = vtk.vtkLineSource()
        line_source2.SetPoint1(self.origin)
        line_source2.SetPoint2(
            self.origin[0] + self.line_pos * self.direction2[0],
            self.origin[1] + self.line_pos * self.direction2[1],
            self.origin[2] + self.line_pos * self.direction2[2],
        )
        line_mapper2 = vtk.vtkPolyDataMapper()
        line_mapper2.SetInputConnection(line_source2.GetOutputPort())

        line_actor2 = vtk.vtkActor()
        line_actor2.SetMapper(line_mapper2)
        line_actor2.GetProperty().SetColor(1, 0, 0)  # Red
        line_actor2.GetProperty().SetLineWidth(2)

        self.red_line_actors = [line_actor1, line_actor2]

        for actor in self.red_line_actors:
            self.renderer.AddActor(actor)

        self.circle_actors.clear()

        for cylinder in self.cylinder_actors:
            x, _, z = cylinder.GetCenter()
            if self.intersects_line(self.origin, self.direction1, (x, 0, z)):
                self.add_intersection_circle(x, self.origin[1], z, self.origin[0] + self.line_pos * self.direction1[0], self.origin[2] + self.line_pos * self.direction1[2])
            if self.intersects_line(self.origin, self.direction2, (x, 0, z)):
                self.add_intersection_circle(x, self.origin[1], z, self.origin[0] + self.line_pos * self.direction2[0], self.origin[2] + self.line_pos * self.direction2[2])

        self.vtkWidget.GetRenderWindow().Render()

    def intersects_line(self, origin, direction, position):
        line_end = [origin[0] + self.line_pos * direction[0],
                    origin[1] + self.line_pos * direction[1],
                    origin[2] + self.line_pos * direction[2]]
        
        sphere_center = position
        distance = ((line_end[0] - sphere_center[0]) ** 2 +
                    (line_end[1] - sphere_center[1]) ** 2 +
                    (line_end[2] - sphere_center[2]) ** 2) ** 0.5

        return distance < 0.03  # Adjusted for consistent overlap

    def add_intersection_circle(self, cx, cy, cz, lx, lz):
        radius = ((lx - cx) ** 2 + (lz - cz) ** 2) ** 0.5
        if radius <= 0.03:  # Circle is only relevant if within the cylinder's radius
            circle_source = vtk.vtkDiskSource()
            circle_source.SetCenter(cx, cy, cz)
            circle_source.SetInnerRadius(0.0)
            circle_source.SetOuterRadius(radius)
            circle_source.SetCircumferentialResolution(50)

            circle_mapper = vtk.vtkPolyDataMapper()
            circle_mapper.SetInputConnection(circle_source.GetOutputPort())

            circle_actor = vtk.vtkActor()
            circle_actor.SetMapper(circle_mapper)
            circle_actor.GetProperty().SetColor(1, 1, 0)  # Yellow

            self.circle_actors.append(circle_actor)
            self.renderer.AddActor(circle_actor)

    def reset_scene(self):
        self.red_line_actors.clear()
        self.circle_actors.clear()
        self.generate_random_origin_and_directions()
        self.add_objects()


    def update_scene(self):
        self.add_objects()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
