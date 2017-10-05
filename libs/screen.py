import mss

s = mss.mss()

def shot():
    img = s.grab(s.monitors[2])
    return img

def save(img, path):
    mss.tools.to_png(img.rgb, img.size, path)
