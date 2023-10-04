


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


MpTerm does not have full ANSI terminal support and will likely never have. At present it supports setting font attributes like foreground and background colors, bold, underline and a few others. Some basic cursormovement it also supported.

![mainwin][mainwin]

## Features
- Basic ANSI Terminal functionality
- Externaly triggered suspend function
- Externaly triggered programing function
- Userdefineable macros
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
Include programdir in path or add the follwing to .bashrc.
``` bash
source mpterm_init
```



## Feature highlights
### Temporary suspend

Temporary suspend is a feature that briefly yield the serialport and therafter automaticly reconnect to it. This is usefefull when you want to allow some another program to access the serialport. For example when developing software for embedded systems a serial port is often used as both debugport and for writing firmware. This feature simplifies the task of "sharing" the serialport betwen debugging and flashing. Suspending can be done in several different ways. The simplest is by pressing the suspend button. However, the port can also be suspended from the commandline which simplifies automation. To suspend MpTerm, simply send the USR1 signal to the process.
``` bash
>kill -s SIGUSR1 pid
```
An alternative to "kill" is to use the builtin function for suspending mpterm. It will automaticly lookup the PID's to all instances of Mpterm and send SIGUSR1 to them.
``` bash
>mpterm --suspend
```
A third way to suspend it to press the suspend button to the left. 

### External program 
Mpterm can also be made to run a external program whithin the terminal itself. During the exectuion of the external program the serial port will be yielded. The external program can be triggerded from a button in the gui by from sending the USR2 signal to mpterm.

To set the external program use the cmdoption `--ext-program` or use setting in UI.
``` bash
>mpterm --ext-program "myprogram --mypoption"
```
To trigger external program use the UI button or use one of the following commands.
``` bash
>mpterm --exec-program
```

``` bash
>kill -s SIGUSR2 pid
```

When plugging and unplugging USB<>serial adapters devicenames have a habit of changing from time to time. This will cause a fixed string external program to stop working. Therefor a macro is provided when defining the external program. `__PORT__` whill be replaced with the port set in the UI.

``` bash
>mpterm --ext-program "avrdude -p atmega328p -P __PORT__"
```

## History

[HISTORY.md](/HISTORY.md)


## ToDo

- Terminal functions
- [ ] Cursor management
- [x] Color encoding (8 colors)
- [x] 256 color encoding
- [ ] Dim text
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
- [ ] Fix color rendering for basic 16 colors
- Feature
- [x] Userdefined quick access macros
- [x] Hexadecimal macros
- [ ] auto repeat macros with intervalsetting
- [x] Settings file
- [ ] Multiple settings profiles
- [x] Echo mode
- [x] Suspend button
- [x] Pause button 
- [ ] Pause history
- [x] Programming button
- [ ] Sync feature
- [x] Hex mode
- [ ] Setting for chars per row in hex mode
- [ ] Show pin status
- [ ] Set pin status
- [ ] Loopback port
- [ ] Manage Bell character
- [ ] copy/paste clipboard
- [ ] Changeable color palets
- [x] Changable newline mode
- [ ] Escape sequence monitor

## Known Issues
- [x] Rendering: Error when <> characters are included
- [ ] Rendering: Text lines overlap with one(maybe two) pixel row(s)
- [ ] Rendering: Terminal rendering performance is slow
- [ ] Rendering: Real bright(bold) colors
- [x] Rendering: Row removal fail
- [ ] UI: Tab cycling is not correct 
- [x] UI: programing mode does not show output from some external programs
- [ ] Feature: Reconnecting to port despite avrdude using the port
- [ ] Hexmode newline error
- [x] Fail when pressing arrow upp/down on Raspberry Pi Pico, CSI.CURSOR_BACK "\e[12D" needs support

## Future ideas

### Plugin system
Enable user to add extra features like protocol analyzers

### Bluetooth 
Support for Bluetooth serialports

### http server
Enable access from network

### Terminal state monitor (mabye as plugin)


### Logg tag 
Define some sort of tag that indicates that data should be redirected to another stream (escape or html) ex. <logg> </logg> or \e[XX for ansi terminal

### Multiple ports open

### Logging function

## License 

## Links
[Serial port monitor](https://www.hhdsoftware.com/serial-port-monitor)

[mainwin]:doc/mainwin.png "mainwin"
