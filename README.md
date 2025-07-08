## Running the code
1. Install all packages needed:
   ```bash
   pip3 install Flask-SocketIO==5.5.1
   pip3 install keyboard==0.13.5
   pip3 install python-dotenv==1.1.1
   pip3 install ultralytics==8.3.152
   pip3 install webcolors==24.11.1
   ```
2. Add a .env file to the project directory `/your/path/Nerfturret/.env`. Add a parameter SERVER_IP and PORT. The file should look like this:
    ```dotenv
    #Replace with your local server ip and the port you want to use
    SERVER_IP=127.0.0.1
    PORT=5555
    ```
3. Make sure both devices(server and client) are connected to the same network
4. Starting the server: `/Nerfturret/Server/` + `py Server.py`(windows) or `python3 Server.py`(linux)
5. Running the turret: `/Nerfturret/Nerfturret/` + `py main.py`(windows) or `python3 main.py`(linux) + [arguments](./README.md#arguments)

## Arguments
`-h`, `--help`: Shows the arguments and their descriptions.

`-i`,`--iteration`: The iterations after an info is printed to the terminal and the Website. Default: `5`

`-c`, `--class`: 
The object or color class which will be detected. Default: `"person"`.  
For more information see [object detection](./README.md#object-detection) and [color detection](./README.md#color-detection)

`-cr`, `-color_range`: The range used to detect around the color. Default: `40`  
For more information see [color detection](./README.md#color-detection)

`-p`, `--pickColor`: If used the user is redirected from the dashboard to a new site. On this site the user can
pick colors. The mean of the selected colors will be detected. Affected by `-cr` 

`-img`, `--show_image`: If used, displays the camera output after detection in a new window. Same as display on website. 

`-v`, `--verbose`: If used, gives more output in the terminal. Affected by `-i`.

`-w`, `--runWebsite`: If used the Turret posts logs, detection pictures and parameters to the website.

## Object detection
Detects different objects. If it is possible to use color detection consider this option. Object detection uses more capacity than color detection and is therefore much slower.

See all object classes that can be detected -> [classes](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml). 

Example: `-c "cell phone"`

## Color detection
Detects different objects based on their color. It's faster than actual object detection. The detection is based on a range around the entered color because
it is very difficult to get the exact color especially due to constantly changing lighting.  
The lower bound color is calculated by subtracting the range value from each rgb value of the entered color.
The upper bound value is calculated the same way but with addition. 

To detect a color enter the name of one of the standard CSS3 colors.

See all colors that can be detected ->  [colors](https://www.w3schools.com/cssref/css_colors.php)

Example: `-c "red"`, `-c "lightblue"`, `-c "blue" -cr 60`
