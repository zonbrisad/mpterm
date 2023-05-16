


<p align="center">
  <img width="150" height="150" src="icons/mp_icon2.png">
</p>

<div style="text-align: center">
<h1>Mpterm</h1>
</div>

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [About](#about)
- [Features](#features)
- [Requirements](#requirements)
  - [Runtime](#runtime)
  - [Development](#development)
- [Install](#install)
  - [Download](#download)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Freqlenty asked Questions](#freqlenty-asked-questions)
- [History](#history)
- [ToDo](#todo)
- [Known Bugs](#known-bugs)
- [Future ideas](#future-ideas)
  - [Plugin system](#plugin-system)
  - [Bluetooth](#bluetooth)
  - [http server](#http-server)
  - [Terminal state monitor (mabye as plugin)](#terminal-state-monitor-mabye-as-plugin)
  - [Quick macro's](#quick-macros)
  - [Logg tag](#logg-tag)
- [Links](#links)
- [Contribute](#contribute)
- [License](#license)
- [Links](#links-1)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## About
MpTerm is a lightweight serial port terminal aimed at embedded development.


MpTerm does not have full ANSII terminal support and will likely never have. At present it supports setting font attributes like foreground and background colors, bold, underline and a few others. Some basic cursormovement it also supported.

![mainwin][mainwin]

## Features
- Basic ANSII Terminal functionality
- Externaly triggered suspend function
- Externaly triggered programing function
- Echo mode
 

## Requirements
- Python 3
- Qt5

## Install

### Download
``` bash
git clone https://github.com/zonbrisad/mpterm.git
```


### Installation

## Functions

### Temporary suspend

MpTerm has a function that causes it to temporary release the port for a short time and thereafter automaticly reconnect. This feature can be usefull if the connected devices can be programmed via the serial port, like for example an Arduino. Suspending can be done in several different ways. The simplest is by pressing the suspend button. However, the port can also be suspended from the commandline which simplifies automation. To suspend MpTerm, simply send the USR1 signal to the process.
``` bash
>kill -s SIGUSR1 pid
```
An alternative to "kill" is to use the builtin function for suspending mpterm. It will automaticly send SIGUSR1 to all instances of mpterm running. 
``` bash
>mpterm --suspend
```


## History

[HISTORY.md](/HISTORY.md)


## ToDo

- [x] Settings file
- [ ] Multiple settings profiles
- [ ] Terminal functions
- [x] Color encoding (8 colors)
- [x] 256 color encoding
- [ ] Truecolor (RGB)
- [ ] Underline style
- [x] Reverse text
- [x] backspace
- [x] tab 
- [x] arrow button support 
- [ ] end 
- [ ] home
- [ ] delete
- [ ] FXX 
- [ ] Cursor management
- [ ] Dim text
- [x] Echo mode
- [x] Suspend button
- [x] Pause button 
- [ ] Pause history
- [x] Programming button
- [ ] Sync feature
- [ ] Hex mode
- [ ] Show pin status
- [ ] Set pin status
- [ ] Loopback port
- [ ] Manage Bell character
- [ ] copy/paste clipboard

## Known Bugs
- [ ] Underline dissapears
- [ ] Real bright(bold) colors
- [ ] anoying Tab cycling 
- [x] programing mode does not show output from avrdude
- [ ] Terminal performance is slow under certain conditions
- [ ] Row removal fail sometimes

## Future ideas

### Plugin system
Enable user to add extra features like protocol analyzers

### Bluetooth 
Support for Bluetooth serialports

### http server
Enable access from network

### Terminal state monitor (mabye as plugin)

### Quick macro's
Add user defined macros for often used sequences

### Logg tag 
Define some sort of tag that indicates that data should be redirected to another stream (escape or html) ex. <logg> </logg> or \e[XX for ansi terminal

### Multiple ports open

### Logging function

## License 

## Links
[Serial port monitor](https://www.hhdsoftware.com/serial-port-monitor)

[mainwin]:doc/mainwin.png "mainwin"
