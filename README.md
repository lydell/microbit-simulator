# Microbit simulator

Incomplete simulator for the Microbit.

Backend in Python, frontend in [Elm]. They speak with each other through
websockets.

The idea is that programs with `import microbit` should Just Work on a computer
with a web browser.

[Elm]: http://elm-lang.org/


## Support

### Backend

- [ ] `microbit.panic`
- [x] **`microbit.reset`**
- [x] **`microbit.sleep`**
- [x] **`microbit.running_time`**
- [ ] `microbit.temperature`
- [ ] `microbit.accelerometer`
- [x] **`microbit.button_a`**
- [x] **`microbit.button_b`**
- [ ] `microbit.compass`
- [x] **`microbit.display`** – Partly (\*)
- [ ] `microbit.i2c`
- [ ] `microbit.Image`
- [ ] `microbit.pin0`–`microbit.pin20`
- [ ] `microbit.spi`
- [ ] `microbit.uart`
- [ ] Other modules than `microbit`

(\*) Regarding `microbit.display`:

- `microbit.display.show(image)` is not supported.
- `microbit.display.show` and `microbit.display.scroll` only support a tiny
  subset of all letters.


### Frontend

- The pixels are emulated.
- Press Left or A to activate the left (A) button.
- Press Right or B to activate the right (B) button.


## Requirements

- Elm 0.17.1
- Python 3.4


## Installation

### Backend

1. Set up a virtual environment the way you prefer it.
2. `pip install -r requirements.txt`

### Frontend

`elm package install`


## Build

`elm make frontend/Main.elm`


## Example

```
$ git clone https://github.com/lydell/microbit-simulator.git
$ git clone https://github.com/lydell/microbit-snake.git
$ cd microbit-snake
$ ln -s ../microbit-simulator/microbit microbit
$ cd ../microbit-simulator
$ python ../microbit-snake/snake.py
$ open index.html
```

## Status

Everything is a work in progress, and everything needs improvements. But at
least the above example is fully runnable.

I did this mainly to play with Elm and websockets, so I might never get around
doing anything more.

See also: <https://github.com/jocke-l/microbit-simulator>


## License

All files are in the public domain.
