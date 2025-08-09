## Project Overview
This project uses a camera to detect classes, either an object or a color. After the successful detection
servos are moved to align and point towards the detected class. This can be used for basic tracking of these classes.


## System Setup

### 1. Raspberry Pi (turret controller)
- Two servos and a camera connected
- Needs to have this repository + the .env file
- Runs the `turret.py` script + [arguments](./README.md#arguments)
- If [optional web dashboard](./README.md#2-optional-web-dashboard-ideal-automatic-outsourced-detection) isn't used, [full single pi](./README.md#3-full-single-pi-setup-not-recommended) setup is used

### 2. Optional web dashboard (ideal, automatic outsourced detection)
- Uses second device that should be more powerful than the Pi
- Must also have this repository cloned + the .env file
- Runs the `server.py` script, which hosts the web-dashboard and
automatically outsources the detection from the Pi to this device

### 3. Full single Pi setup (not recommended)
- Runs `server.py` and `turret.py` + [arguments](./README.md#arguments) simultaneously on the Raspberry Pi
- High demand on the Pi causes much slower detection

## Running the code
1. Install all packages needed:
   ```bash
   pip3 install -r requirements.txt
   ```
2. Add a .env file to the project directory `/your/path/Nerfturret/.env`. Add a following parameters. The file should look like this:
   ```dotenv
    SERVER_IP=127.0.0.1 # Replace with your local server ip
    PORT=5555 # Replace with the port you want to use
    CAMERA_INDEX=0 # The camera used for detection
    
    # adjust for the camera in use, width and height can be 640 by 480
    # bandwidth is necessary to be configured
    # (server.py only needs the following section)
    CAMERA_WIDTH=640
    CAMERA_HEIGHT=480
    CAMERA_BANDWIDTH_WIDTH_ANGLE=50
    CAMERA_BANDWIDTH_HEIGHT_ANGLE=25
    
    #Replace with the Pins used by the Pi
    X_SERVO_PIN=2
    Y_SERVO_PIN=17
    CHARGE_PIN=4
    LOAD_PIN=3
    ```

3. (If used) Starting the server: `/Nerfturret/server/` + `py server.py`(windows) or `python3 server.py`(linux)
4. Running the turret: `/Nerfturret/turret/` + `py turret.py`(windows) or `python3 turret.py`(linux) + [arguments](./README.md#arguments), -> see [examples](./README.md#examples)

## Arguments
`-h`, `--help`: Shows the arguments and their descriptions.

`-i`,`--iteration`: The iterations after an info is printed to the terminal and the Website. Default: `5`

`-c`, `--class`: 
The object or color class which will be detected. Default: `"person"`.  
For more information see [object detection](./README.md#object-detection) and [color detection](./README.md#color-detection)

`-cr`, `-color_range`: The range used to detect around the color. Default: `40`  
For more information see [color detection](./README.md#color-detection)

`-p`, `--pickColor`: If used the user is redirected from the dashboard to a new site. On this site the user can
pick colors. The mean of the selected colors will be detected. Affected by `-cr`. Only works when website is running(`-rw` enabled).

`-img`, `--show_image`: If used, displays the camera output after detection in a new window. Same as display on website. 
The window is displayed on the device the detection is done.

`-v`, `--verbose`: If used, more output in the terminal is given. Affected by `-i`.

`-rw`, `--runWebsite`: If used, it tries to establish a connection to the server device. Necessary for the
[web dashboard hosting](./README.md#2-optional-web-dashboard-ideal-automatic-outsourced-detection)

## Object detection
Detects different objects. If it is possible to use color detection consider this option. Object detection uses more capacity than color detection and is therefore much slower.

See all object classes that can be detected -> [classes](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml). 

Example: `-c "cell phone"`

## Color detection
Detects different objects based on their color. It's faster than actual object detection. The detection is based on a range around the entered color because
it is very difficult to detect an exact color especially due to constantly changing lighting.  
The lower bound color is calculated by subtracting the range value from each rgb value of the entered color.
The upper bound value is calculated the same way but with addition. 

To detect a color enter the name of one of the standard CSS3 colors.

See all colors that can be detected ->  [colors](https://www.w3schools.com/cssref/css_colors.php)

Example: `-c "#187659"`, `-c "lightblue"`, `-c "blue" -cr 60`

## Examples
These are examples to start the turret:
1. `sudo python3 turret.py -i 1 -cr 30 -c "#187659" -rw`
 
   Prints output per detection cycle. 

   Detects the color from a green red bull can (color might vary due to different light setting). 

   Uses website (server device needed, can be bypassed by removing -rw).


2. `sudo python3 turret.py -i 1 -p -rw`

   Prints output per detection cycle. 
   
   Website required (server device needed).

   Uses the color picker to determine detection color.

3. `sudo python3 turret.py -i 1 -c "cell phone" -rw`

   Prints output per detection cycle. 
   
   Uses website (can also be disabled).

   Detects cell phones.