
import serial
import numpy


class Chamber:
    _BITS = 13


    def __init__(self, port, baudRate = 115_200, dataBits = 8, parity = 'N', stopBits = 1):
        self._uart = serial.Serial(port, baudrate = baudRate, bytesize = dataBits, parity = parity, stopbits = stopBits, timeout = 0)
        self._synced = False
        self._error = False
        self._buffer = []


    @property
    def error(self):
        return self._error

    
    def read(self):
        measurements = []

        if self._uart.in_waiting > 0:
            self._buffer.extend(list(self._uart.read(self._uart.in_waiting)))

            if not self._synced and len(self._buffer) >= 4:
                for i in range(len(self._buffer) - 3):
                    if (self._buffer[i] & 0xC0) == 0xC0 and (self._buffer[i + 1] & 0xC0) == 0 and (self._buffer[i + 2] & 0xC0) == 0 and (self._buffer[i + 3] & 0xC0) == 0:
                        self._synced = True
                        self._buffer = self._buffer[i:]
                        break

            if self._synced:
                while len(self._buffer) >= 4:
                    if (self._buffer[0] & 0xC0) != 0xC0 or (self._buffer[1] & 0xC0) != 0 or (self._buffer[2] & 0xC0) != 0 or (self._buffer[3] & 0xC0) != 0:
                        self._synced = False
                        self._error = True
                        break
                    else:
                        t1 = (((self._buffer[1] & 0x1F) << 6) | (self._buffer[0] & 0x3F)) / 16.
                        t2 = (((self._buffer[3] & 0x1F) << 6) | (self._buffer[2] & 0x3F)) / 16.
                        
                        if (self._buffer[1] & 0x40):
                            t1 = -t1

                        if (self._buffer[1] & 0x40):
                            t2 = -t2

                        measurements.append([t1, t2])

                        self._buffer = self._buffer[4:]

        return measurements


    def write(self, power0, power1):
        sign0 = (power0 < 0) * 0x40
        sign1 = (power1 < 0) * 0x40

        power0 = numpy.abs(power0)
        power1 = numpy.abs(power1)

        power0 = min(1., power0)
        power1 = min(1., power1)

        binary0 = int(numpy.round(power0 * (2 ** self._BITS - 1)))
        binary1 = int(numpy.round(power1 * (2 ** self._BITS - 1)))

        lsb0 = (binary0 & 0x7F) | 0xC0
        msb0 = (binary0 >> 7) | sign0

        lsb1 = (binary1 & 0x7F)
        msb1 = (binary1 >> 7) | sign1

        self._uart.write(bytearray([lsb0, msb0, lsb1, msb1]))
