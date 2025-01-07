#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 
@author: juliengautier(LOA)
inspired from devantech pip install 
user = admin
password : password
"""

import socket

class RELAY():

    def __init__(self, ip = "10.0.1.79", port = 17494, password  = None, moduleID = 18):   
        """
        Parameters:
                ip (string): The IP address of the module
                port (int): The port number of the module
                password (string): The password used to unlock the module
                moduleID 18 for ETh002
                for conection to web interface : user admin password password
        """

        self.module_id = moduleID
        self.ip = ip
        self.port = port
        self.password = password
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self):
        """
        Tries to connect to an ETH module.

        If a connection is established it validates the module ID to make sure that we are talking to the right kind of module and then sends the password.
        """
        try:
            self.socket.connect((self.ip, self.port))
            print('Connected to relay @ ',self.ip,'on port : ', self.port)
        except:
            raise
        if self.checkModuleID() != True:
            self.close()
            raise Exception("Received unexpected ID from module.")
        
        if self.isPasswordEnabled() == True:
            if self.sendPassword() == False:
                self.close()
                raise Exception("Wrong password sent to module.")
           
    def checkModuleID(self):
        """
        Checks the module is of the expected type.

        Returns:
            bool: true if the correct module is found false otherwise.
        """
        self.write(b'\x10')
        d = self.read(3)
        if d[0] != self.module_id:
            return False
        return True

    def isPasswordEnabled(self):
        """
        Checks to see if the password is enabled.

        Returns:
            bool: True if the password is enabled, false otherwise.
        """
        self.write(b'\x7a')
        d = self.read(1)
        if d[0] == 0:
            return True
        return False

    def sendPassword(self):
        """
        Sends the password to the module and checks for success.

        Returns:
            bool: True is accepted, false otherwise.
        """
        pw = b'\x79' + bytes(self.password, "ascii")
        self.write(pw)
        d = self.read(1)
        if d[0] != 1:
            return False
        return True 
    
    def close(self):
        """
        Closes the connection to a module.
        """
        self.socket.close()

    def write(self, message):
        """
        Writes data out to a module.
        Parameters:
            message (string): The data to write.
        """
        try:
            self.socket.sendall(message)
        except:
            raise
            
    def read(self, number):
        """
        Reads data back from a module.

        Parameters:
            number (int): The number of bytes to read.

        Returns:
            array: The data received.
        """
        chunks = []
        bytes_received = 0
        while bytes_received < number:
            try:
                chunk = self.socket.recv(2048)
                if chunk == '':
                    raise Exception("Unable to read the expected number of bytes")
                chunks.extend(chunk)
                bytes_received = bytes_received + len(chunk)
            except:
                raise
        return chunks
    def getSerialNumber(self):
        """
        Gets the serial number from the module.

        Returns:
            array: The 5 byte mac address read back from the module.
        """
        self.write(b'\x77')
        return self.read(6)

    def getVolts(self):
        """
        Reads the voltage back from the module.

        Returns:
            float: the voltage.
        """
        self.write(b'\x78')
        d = self.read(1)
        vl = d[0] / 10
        return vl

    def getModuleInfo(self):
        """
        Gets the module info.

        Returns:
            array: the module ID, hardware and firmware versions.
        """
        self.write(b'\x10')
        d = self.read(3)
        return d
    
    def getDigitalOutputs(self):
        """
        Get an array that represents the states of the digital outputs.

        Returns:
            array: Bytes indicating the states of the outputs.
        """
        self.write(b'\x24')
        d = self.read(1)
        return d
    
    def getDO1State(self):
        """
        Get the state of digital output 1.

        Returns:
            int: 1 for active 0 for inactive
        """
        d = self.getDigitalOutputs()
        st = 1 if d[0] & 0b00000001 else 0
        return st

    def getDO2State(self):
        """
        Get the state of digital output 2.

        Returns:
            int: 1 for active 0 for inactive
        """
        d = self.getDigitalOutputs()
        st = 1 if d[0] & 0b00000010 else 0
        return st
    
    def digitalActive(self, port, pulse):
        """
        Set a digital output active.

        Parameters:
            port (int): The digital io port to set.
            pulse (int): The pulse time for the change.
        """
        message = "\x20"
        message += chr(port)
        message += chr(pulse)
        self.write(bytes(message, "utf-8"))
        d = self.read(1)
                
    def digitalInactive(self, port, pulse):
        """
        Set a digital output inactive.

        Parameters:
            port (int): The digital io port to set.
            pulse (int): The pulse time for the change.
        """
        message = "\x21"
        message += chr(port)
        message += chr(pulse)
        self.write(bytes(message, "utf-8"))
        d = self.read(1)

    def setDigitalState(self, port, pulse, state):
        """
        Set the state of a digital output.

        Parameters:
            port (int): The digital output to set.
            pulse (int): The pulse time for the change.
            state (int): The state to set, 0 for inactive, otherwise active.
        """
        if state == 0:
           self.digitalInactive(port, pulse)
        else:
            self.digitalActive(port, pulse)

    def setDO1Active(self):
        """
        Sets digital output 1 to active.
        """
        self.digitalActive(1, 0)

    def setDO2Active(self):
        """
        Sets digital output 2 to active
        """
        self.digitalActive(2, 0)

    def setDO1Inactive(self):
        """
        Sets digital output 1 to inactive.
        """
        self.digitalInactive(1, 0)
    
    def setDO2Inactive(self):
        """
        Sets digital output 2 to inactive
        """
        self.digitalInactive(2, 0)  

    def getDO1State(self):
        """
        Get the state of digital output 1.

        Returns:
            int: 1 for active 0 for inactive
        """
        d = self.getDigitalOutputs()
        st = 1 if d[0] & 0b00000001 else 0
        return st

    def getDO2State(self):
        """
        Get the state of digital output 2.

        Returns:
            int: 1 for active 0 for inactive
        """
        d = self.getDigitalOutputs()
        st = 1 if d[0] & 0b00000010 else 0
        return st

if __name__ == "__main__":
    mod = RELAY(ip = "10.0.1.79", port = 17494)
    mod.connect()
    print(mod.getModuleInfo())
    mod.setDO1Inactive()
    print(mod.getDO1State(), mod.getDO2State(), mod.getSerialNumber())
    mod.close()