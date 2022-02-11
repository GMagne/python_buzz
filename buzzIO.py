import usb.core
import usb.util
import traceback, sys, os
import time
import array

class buzz:
	def __init__ (self):
		# ID 054c:1000 Sony Corp. Wireless Buzz! Receiver
		self.device = usb.core.find(idVendor=0x054c, idProduct=0x1000)
		self.lights = [0,0,0,0]
		self.buttons = [{'R':0, 'Y':0, 'G':0, 'O':0, 'B':0}, {'R':0, 'Y':0, 'G':0, 'O':0, 'B':0}, {'R':0, 'Y':0, 'G':0, 'O':0, 'B':0}, {'R':0, 'Y':0, 'G':0, 'O':0, 'B':0}]
		self.bits = 0

		if self.device is None:
			raise ValueError('Device not found')


		self.device.set_configuration()
		#usb.util.claim_interface(self.device, 0)
		cfg = self.device.get_active_configuration()
		self.endpoint = cfg[(0,0)][0]


	def writelights(self):
		self.device.ctrl_transfer(0x21, 0x09, 0x0200,0,[0x0,self.lights[0],self.lights[1],self.lights[2],self.lights[3],0x0,0x0])

	def setlights(light_array):
		self.lights[0] = 0xFF if light_array[0] & 1 else 0x00
		self.lights[1] = 0xFF if light_array[1] & 1 else 0x00
		self.lights[2] = 0xFF if light_array[2] & 1 else 0x00
		self.lights[3] = 0xFF if light_array[3] & 1 else 0x00

	def readcontrollers(self, raw = 0, timeout = None):
		# Reads the controller
		# Returns the result of Parsecontroller (the changed bit) or raw

		try: 
			#cfg = self.device.get_active_configuration()
			#self.endpoint = cfg[(0,0)][0]
			data = array.array('B', (127, 127, 0, 0, 240))
			self.device.read(self.endpoint.bEndpointAddress, data , timeout=None)
			parsed = self.parsecontroller(data)
		except usb.core.USBError:
			data = None

		if data != None and raw == 0:
			data = parsed

		return data

	def parsecontroller(self, data):
		# Function to parse the results of readcontroller
		# We break this out incase someone else wants todo something different
		# Returns the changed bits

		# Controller 1
		self.buttons[0]["R"] = 1 if data[2] & 1 else 0
		self.buttons[0]["Y"] = 1 if data[2] & 2 else 0
		self.buttons[0]["G"] = 1 if data[2] & 4 else 0
		self.buttons[0]["O"] = 1 if data[2] & 8 else 0
		self.buttons[0]["B"] = 1 if data[2] & 16 else 0

		# Controller 2
		self.buttons[1]["R"] = 1 if data[2] & 32 else 0
		self.buttons[1]["Y"] = 1 if data[2] & 64 else 0
		self.buttons[1]["G"] = 1 if data[2] & 128 else 0
		self.buttons[1]["O"] = 1 if data[3] & 1 else 0
		self.buttons[1]["B"] = 1 if data[3] & 2 else 0

		# Controller 3
		self.buttons[2]["R"] = 1 if data[3] & 4 else 0
		self.buttons[2]["Y"] = 1 if data[3] & 8 else 0
		self.buttons[2]["G"] = 1 if data[3] & 16 else 0
		self.buttons[2]["O"] = 1 if data[3] & 32 else 0
		self.buttons[2]["B"] = 1 if data[3] & 64 else 0

		# Controller 4
		self.buttons[3]["R"] = 1 if data[3] & 128 else 0
		self.buttons[3]["Y"] = 1 if data[4] & 1 else 0
		self.buttons[3]["G"] = 1 if data[4] & 2 else 0
		self.buttons[3]["O"] = 1 if data[4] & 4 else 0
		self.buttons[3]["B"] = 1 if data[4] & 8 else 0

		oldbits = self.bits
		self.bits = (data[4] << 16) + (data[3] << 8) + data[2]

		changed = oldbits | self.bits

		return changed

	def getbuttons(self):
		# Returns current state of buttons
		self.readcontrollers()
		return self.buttons

	def getlights(self):
		# Returns the current state of the lights
		return self.lights

	def __del__(self):
		usb.util.release_interface(self.device, 0)
		

io = buzz()
