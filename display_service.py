import SH1106
import time, random
import RPi.GPIO as GPIO
from PIL import Image,ImageDraw,ImageFont
import os
import systemd.daemon

#region constants
FAN_ON_TEMPERATURE = 72
FAN_OFF_TEMPERATURE = 65
USE_EXT_DISPLAY = True
FONT_SIZE = 12
FONT_SPACING = round(FONT_SIZE * 0.85)
COOLER_PIN = 15
#endregion

disp = None
font = None
offsets = None

class Offsets(object):
    def __init__(self, freq = 3, maxX = 20, maxY = 10):
      self.x = 0
      self.y = 0
      self.maxX = maxY
      self.maxY = maxY
      self.ts = 0
      self.freq = freq if freq != None else 3

    def offsets(self):
      now = time.time()
      if self.ts + self.freq < now:
        self.ts = now
        self.x = random.randint(0, self.maxX)
        self.y = random.randint(0, self.maxY)
      return (self.x, self.y)
    
def get_cpu_times():
  """Read CPU times from /proc/stat."""
  with open('/proc/stat', 'r') as f:
      lines = f.readlines()
  # Get the first line, which corresponds to the overall CPU stats
  cpu_line = lines[0].strip().split()
  # Convert values to integers (ignore the first element 'cpu')
  return list(map(int, cpu_line[1:]))

def calculate_cpu_usage(previous, current):
  """Calculate the CPU usage percentage."""
  prev_idle = previous[3]  # Idle time
  curr_idle = current[3]
  
  prev_total = sum(previous)
  curr_total = sum(current)
  
  # Calculate usage
  idle = curr_idle - prev_idle
  total = curr_total - prev_total
  usage = 100 * (total - idle) / total
  
  return usage

def display_stdout(cpu_usage, temperature, fan_on):
  print(f"Current CPU Usage: {cpu_usage:.2f}%")
  print(f"cpu temperature: {temperature:.2f}")
  print(f"Fan on: {fan_on}")

def display_ext_display(cpu_usage, temperature, fan_on):
  global disp
  global font
  global offsets

  # Create blank image for drawing.
  image1 = Image.new('1', (disp.width, disp.height), "WHITE")
  draw = ImageDraw.Draw(image1)
  
  # draw line
  # draw.line([(0,0),(127,0)])
  # draw.line([(0,0),(0,63)])
  # draw.line([(0,63),(127,63)], fill = 0)
  # draw.line([(127,0),(127,63)], fill = 0)

  # draw text
  # Случайный сдвиг надписей каждые несколько секунд, чтобы не выжигать дисплей OLED:
  (offsetX, offsetY) = offsets.offsets()
  cpu_usage = round(cpu_usage)
  fan = "on" if fan_on else "off"
  draw.text((0 + offsetX, FONT_SPACING * 0 + offsetY), f"CPU: {cpu_usage}%", font = font, fill = 0)
  draw.text((0 + offsetX, FONT_SPACING * 1 + offsetY), f"temp: {temperature:.1f} C", font = font, fill = 0)
  draw.text((0 + offsetX, FONT_SPACING * 2 + offsetY), f"Fan {fan}", font = font, fill = 0)

  image1=image1.rotate(180) 
  disp.ShowImage(disp.getbuffer(image1))

def start_fan_stdout():
  print("========> Fan started")

def stop_fan_stdout():
  print("========> Fan stopped")

def start_fan_gpio():
  GPIO.output(COOLER_PIN, GPIO.HIGH)

def stop_fan_gpio():
  GPIO.output(COOLER_PIN, GPIO.LOW)

display = display_ext_display if USE_EXT_DISPLAY else display_stdout
stop_fan = stop_fan_gpio if USE_EXT_DISPLAY else stop_fan_stdout
start_fan = start_fan_gpio if USE_EXT_DISPLAY else start_fan_stdout

def read_temperature():
  with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
    return int(f.read()) / 1000


def init():
  if not USE_EXT_DISPLAY:
    return
  global disp
  global font
  global offsets
  offsets = Offsets(maxX = 30, maxY = 40, freq = 3)
  disp = SH1106.SH1106()
  disp.Init()
  # Clear display.
  disp.clear()
  fontFile = os.path.dirname(os.path.realpath(__file__)) + "/Font.ttf"
  # fontFile = "AnkaCoder-C75-r.ttf"
  # fontFile = "AnkaCoder-C87-r.ttf"
  font = ImageFont.truetype(fontFile, FONT_SIZE)
  GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
  GPIO.setup(COOLER_PIN, GPIO.OUT, initial = GPIO.LOW)   # Set pin to be an output pin and set initial value to low (off)

if __name__ == "__main__":
  init()
  previous_times = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  fan_on = False
  systemd.daemon.notify('READY=1')
  while True:
    time.sleep(1)  # Wait for 1 second
    # Get initial CPU times``
    current_times = get_cpu_times()
    
    # Calculate and print CPU usage
    cpu_usage = calculate_cpu_usage(previous_times, current_times)
    temperature = read_temperature()
    if temperature > FAN_ON_TEMPERATURE and not fan_on:
      start_fan()
      fan_on = True
    if temperature <= FAN_OFF_TEMPERATURE and fan_on:
      stop_fan()
      fan_on = False

    display(cpu_usage, temperature, fan_on)
    previous_times = current_times
