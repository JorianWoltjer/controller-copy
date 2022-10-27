# Controller Copy

Copy inputs of a Keyboard, PS4 Controller or Xbox Controller to multiple virtual controllers. It can basically copy your inputs as another local player. 

Originally made for Rocket League, but can be applied to other games and controls by changing the code in [`input_methods.py`](input_methods.py) to map
inputs to different controls.

## Demo Video

[![A video showcasing 4 players on one screen moving exactly in sync](https://img.youtube.com/vi/tG9pW9u5CfY/maxresdefault.jpg)](https://www.youtube.com/watch?v=tG9pW9u5CfY)

## How do I use it?

First, clone and unpack this repository. Then the `main.py` script will be the script you use to create and run the controllers. 

```Shell
git clone https://github.com/JorianWoltjer/controller-copy.git && cd controller-copy
pip install -r requirements.txt  # Install necessary dependencies

python main.py  # Run script
```

It always creates **Xbox** Controllers, but you can choose one of 3 options where it gets the inputs from:

* Keyboard (default): `KeyboardInput()`
* PS4 Controller: `PS4ControllerInput()`
* Xbox Controller: `XboxControllerInput()`

To select one of these, you must change the code in [`main.py`](main.py). At the top of the file there are 3 `INPUT`s, and one of them needs to be uncommented (remove the `#`). This one is then used, and the code will automatically adjust to work correctly with that device. 

You can also choose the number of controllers with the `EXTRA_CONTROLLERS` variable. This will determine how many extra players you would want. For example in a game with 4 players, you are one of them, so to fill it you would select 3. 

## Controls

While the script is running, you have some more controls to configure what controllers are active on the fly!

You can use the numpad to do this. The `0` key is special, it enabled every controller connected. Then the rest of the 
numbers just activate only the controller with that specific number. This is so you can target a specific player
to do some action, if you don't want all the others to copy. This is especially useful if the players become
**desynced** from eachother for some reason. For example:

* Numpad `1`: Enable only the first virtual controller, disable all the rest
* Numpad `2`: Enable only the second virtual controller, disable all the rest
* etc.

## Troubleshooting

It might be a bit finicky to get working, so here are some quick answers to a few questions.

### Why does it not work on Linux?

* I have not tested on Linux, but it is likely the Xbox controllers that `pyxinput` creates need some drivers, or won't work at all. The mouse buttons are also implemented with the `win32api`, so this would likely need to be replaced for Linux to work

### Inputs are going crazy?!?

* Firstly, make sure you are using a PS4 controller with the PS4 input, and an Xbox Controller with the Xbox controller. The code assumes you do this correctly, meaning when you don't it will read inputs from nonsense, outputting nonsense as well
* All input methods are tested with my own devices, so a different device might behave differently enough to make the code not work anymore. Especially the PS4 input which I have implemented from a very low level with reading bits from the gamepad, is likely to break with other controllers. If you are experienced with Python however, you might be able to implement this yourself by looking at the `hid` output and guessing what bits correspond to what buttons and values on the controller. 
