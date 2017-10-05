# Hearthstone - Tensorflow Object Detection

**This project is WIP**

**Linux only tested !**

# Description
This is a tool to collect Hearthstone data and feed with this the [Tensorflow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection).

# Getting starting

## Collector
The collector will collect images with labels while playing, complete automatic.
Its collect the battlefield, arena draft and the collection.

Set game to fullscreen 1920x1080 and start the collector:

```python3 collect.py```

After the collector got a new labeled image, the labelImg application starts and shows you the result.
You can edit the labels and save, press **ctrl+alt+z** to delete it or just keep playing if the result is fine.

### Battlefield
The collector gather the images after every own turn.

### === NOT YET IMPLEMENTED: ===
### Arena
The collector gather the images after every card pick.

### Collection
The collector don't start automatic, you have to start the process with **ctrl+alt+g** if you want to stop it press **ctrl+alt+s**.
It's recommended that you set the view of collection to **wild cards**, **crafting** and **Include Uncraftable Cards** like this:
![collection_example](https://github.com/TheCherry/hsdetect/docs/collection.png)

# Known Bugs
* Gather the battlefield vs the Innkeeper is to late.

# License
MIT License

Copyright (c) 2017 Dee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
