# Copyright 2008 Jim Bridgewater

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# 10/16/08 Jim Bridgewater
# Changed code to only import labjacku12 when running under windows.

# 6/19/08 Jim Bridgewater
# Changed constructor so that is does not try to setup the DIOs if the labjack
# is not found.

# 6/17/08 Jim Bridgewater
# Changed constructor so that it does not call sys.exit() if the labjack is not
# found.

# 6/13/08 Jim Bridgewater
# Added step_time and settle_time parameters.

# 6/04/08 Jim Bridgewater
# Changed to conform to PEP8 python style guide.

# 5/14/08 Jim Bridgewater
# Created this class to allow multiple stepper motors to use
# the same code.

# 5/13/08 Jim Bridgewater
# Created this module to provide an easy interface to the
# Portescap 20MO20DIU stepper motor.  Each step moves the 
# shaft of this motor 18 degrees.  This module interfaces
# with the LabJack U12 which provides four digital outputs 
# that drive the four p channel MOSFETs controlling current
# flow through the stepper motors windings.

# Create a class for the Portescap stepper motor.  It needs to have
# a property to keep track of which 4 LabJack DIOs each instance
# will use to control its motor.  The motor requires 4 inputs (1 nibble)
# and there are 16 DIOs so the nibble input should be 0, 1, 2, or 3.

############################################################
# import modules
############################################################

import sys, time, os
from errors import Error

if os.name == 'nt':
  import labjacku12
else:
  import labjacku12_dummy as labjacku12

power_transistors = "ntype"
#power_transistors = "ptype"

############################################################
# The methods defined in this class are:
############################################################
# step_clockwise(steps)
# step_counterclockwise(steps)
# turn_power_off()

class Portescap20MO20DIU:
  # The class constructor sets up the control signals to be outputs,
  # sets the signals high so no current flows, and defines the sequence 
  # of states that produces rotation of the motor.  Stepping through 
  # these states from left to right produces clockwise rotation, stepping 
  # through them from right to left produces counter clockwise rotation.
  def __init__(self, nibble, step_time = 0.1, settle_time = 0.1):
    self.nibble = nibble
    self.step_time = step_time
    self.settle_time = settle_time
    if labjacku12.check_connection() == 0:
      raise Error("The LabJack used to control the Portescap " \
      "20MO20DIU stepper motor is not responding.")
    Outputs = 0xf << (4 * nibble)
    InitialValue = 0xf << (4 * nibble)
    labjacku12.set_DIO_to_output(Outputs, InitialValue)
    if power_transistors == "ptype":
      self.states = [0x9, 0x5, 0x6, 0xa]  # for p-type transistors
      self.off = 0xf
    else:
      self.states = [0x6, 0xa, 0x9, 0x5]  # for n-type transistors
      self.off = 0x0
  # The Clockwise method rotates the motor the specified number of steps
  # in the clockwise direction.  The Portescap 20MO20DIU moves 18 degrees
  # for each step.
  def step_clockwise(self, steps):
    # make sure the motor is energized in its current state
    labjacku12.write_to_DIO(self.states[0] << (4 * self.nibble), \
    0xf << (4 * self.nibble))
    for i in range(steps):
      # rotate the states for clockwise rotation
      self.states.append(self.states.pop(0))
      # energize the next state
      labjacku12.write_to_DIO(self.states[0] << (4 * self.nibble), \
      0xf << (4 * self.nibble))
      time.sleep(self.step_time)
    # wait for motor to stop moving
    time.sleep(self.settle_time)
    # turn all 4 outputs off so no current flows
    labjacku12.write_to_DIO(self.off << (4 * self.nibble), \
    0xf << (4 * self.nibble))
  # The CounterClockwise method rotates the motor the specified number of 
  # steps in the counter clockwise direction.  The Portescap 20MO20DIU 
  # moves 18 degrees for each step.
  def step_counterclockwise(self, steps):
    # make sure the motor is energized in its current state
    labjacku12.write_to_DIO(self.states[0] << (4 * self.nibble), \
    0xf << (4 * self.nibble))
    for i in range(steps):
      # rotate the states for counter clockwise rotation
      self.states.insert(0, self.states.pop())
      # energize the next state
      labjacku12.write_to_DIO(self.states[0] << (4 * self.nibble), \
      0xf << (4 * self.nibble))
      time.sleep(self.step_time)
    # wait for motor to stop moving
    time.sleep(self.settle_time)
    # turn all 4 outputs off so no current flows
    labjacku12.write_to_DIO(self.off << (4 * self.nibble), \
    0xf << (4 * self.nibble))
  # The PowerOff method sets all four outputs high so that the stepper motor
  # doesn't draw any current.
  def turn_power_off(self):
    labjacku12.write_to_DIO(self.off << (4 * self.nibble), \
    0xf << (4 * self.nibble))

