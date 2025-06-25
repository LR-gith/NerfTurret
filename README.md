## Running the code
If you want to run it on a Raspberry Pi with pin control you need to run the code with the necessary arguments(below).

## Arguments
There are currently the arguments to configure.

`-h`, `--help`: Shows the arguments and thier descriptions.

`-i`,`--iteration`: The iterations after an info is printed to the Termianl. Default: `5`

`-c`, `--class`: The object class which is detected. Default: `person`, Example: `cell phone`. All classes -> [classes](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml)

`-pi`, `--runningOnPi`: Enables the mode to run the code on a Pi.

## Examples
Each line requires `py .\main.py` for windows and `python3 main.py` for linux infront of the arguments. Also the current path needs to be `/NerfTurret/NerfTurret`.

Run the code with 5 iterations per terminal output, detecting  persons and running not on a pi ` ` (no additional arguments)

Run the code with 2 iterations per terminal output, detecting  persons and running not on a pi `-i 2`

Run the code with 5 iterations per terminal output , detecting  phones and running not on a pi `-i 5 -c "cell phone"`

Run the code with 5 iterations per terminal output , detecting  persons and running on a pi `-i 5 -c "cell phone" -pi`


## Optimal for Testing
Not on pi: `-i 15 -c "cell phone"`

On pi: `-i 1 -c "cell phone" -pi` 
