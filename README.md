## Running the code
If you want to run it on a Raspberry Pi with pin control you need to first undo the commented import in PiController line 1.
Then run the code with the necessary arguments(below).

## Arguments
There are currently three arguments to configure.
1. After which iteration an info is printed to the Termianl. Example `5`(default) , `15`
2. The object class which is detected. Example `person`(default), `cell phone`. All classes -> [classes](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml)
3. The configuration if running on a Pi. `-onPi`

It isn't possible to only configure a single argument except it is the first one. So if you want to configure an argument, 
all the arguments before must be specified.

## Examples
Each line requires `py .\main.py` for windows and `python3 main.py` for linux infront of the arguments. Also the current path needs to be `/NerfTurret/NerfTurret`.

Run the code with 5 iterations per terminal output, detecting  persons and running not on a pi ` ` (no additional arguments)

Run the code with 2 iterations per terminal output, detecting  persons and running not on a pi `2`

Run the code with 5 iterations per terminal output , detecting  phones and running not on a pi `5 "cell phone"`

Run the code with 5 iterations per terminal output , detecting  persons and running on a pi `5 "cell phone" -onPi`


## Optimal for Testing
Not on pi: `15 "cell phone"`

On pi: `1 "cell phone" -onPi` 
