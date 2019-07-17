# perception
This project is aiming to create a perception system for robot manipulator
# Project is under-developing

# Things to do before running code
1. Install Apache-fuseki server
2. Install Tensorflow
3. Install Librealsense 2
4. Install Flask

# Running code
Run each line below in seperate terminal tab
```sh
roslaunch rosbridge_server rosbridge_websocket.launch
rosrun robot_vision server.py
```
Run ontology server
```sh
cd path/apache-fuseki
./fuseki-server
```
Run object detection
```sh
rosrun robot_vision testing_detecion.py
```
