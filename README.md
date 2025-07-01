## Running the code
Starting the Server: `/Nerfturret/Server/` + `py Server.py`(windows) or `python3 Server.py`(linux)

Running the turret: `/Nerfturret/Server/` + `py main.py`(windows) or `python3 Server.py`(linux) + arguments

## Arguments
`-h`, `--help`: Shows the arguments and their descriptions.

`-i`,`--iteration`: The iterations after an info is printed to the terminal and the Website. Default: `5`

`-c`, `--class`: 
The object or color class which will be detected. Default: `"person"`.  
For more information see [object detection](./README.md#object-detection) and [color detection](./README.md#color-detection)

`-cr`, `-color_range`: The range used to detect around the color. Default: `40`  
For more information see [color detection](./README.md#color-detection)

`-img`, `--show_image`: If used, displays the camera output after detection in a new window. Same as display on website. 

`-v`, `--verbose`: If used, gives more output in the terminal. Affected by `-i`.

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

## Optimal for testing
Not on pi: `-i 15 -c "cell phone"`

On pi: `-i 1 -c "cell phone" -pi` 
