#include <OneWire.h>

// Settings

uint16_t peltier0h = 18;
uint16_t peltier0c = 19;
uint16_t peltier1h = 22;
uint16_t peltier1c = 23;

uint16_t sensor0 = 13;
uint16_t sensor1 = 14;

uint8_t  resolution = 13;
double   frequency  = 10000;

OneWire ds0(sensor0);
OneWire ds1(sensor0);

// Code

int t0;
int t1 = millis();

void setup(void) 
{
    Serial.begin(115200);

    ledcSetup(0, frequency, resolution);
    ledcAttachPin(peltier0h, 0);

    ledcSetup(1, frequency, resolution);
    ledcAttachPin(peltier0c, 1);

    ledcSetup(2, frequency, resolution);
    ledcAttachPin(peltier1h, 0);

    ledcSetup(3, frequency, resolution);
    ledcAttachPin(peltier1c, 1);
}

void loop(void)
{
    if (Serial.available() >= 4)
    {
        uint8_t packet[4];

        packet[0] = Serial.read();
        
        if (!(packet[0] >> 7))
            return;
        
        for (int i = 1; i < 4; i++)
        {
            packet[i] = Serial.peek();

            if (packet[i] >> 7)
                return;

            Serial.read();
        }
        
        uint32_t dutyCycle0 = ((static_cast<uint32_t>(packet[1]) & 0x3F) << 7) | (static_cast<uint32_t>(packet[0]) & 0x7F);
        uint32_t dutyCycle1 = ((static_cast<uint32_t>(packet[3]) & 0x3F) << 7) | (static_cast<uint32_t>(packet[2]) & 0x7F);
        
        bool polarity0 = packet[1] & 0x40;
        bool polarity1 = packet[3] & 0x40;

        if (polarity0)
        {
            ledcWrite(0, 0);
            ledcWrite(1, dutyCycle0);
        }
        else
        {
            ledcWrite(0, dutyCycle0);
            ledcWrite(1, 0);
        }
        
        if (polarity1)
        {
            ledcWrite(2, 0);
            ledcWrite(3, dutyCycle1);
        }
        else
        {
            ledcWrite(2, dutyCycle1);
            ledcWrite(3, 0);
        }
    }

    t0 = millis();

    if (t0 - t1 > 750)
    {
        byte data0[12];
        byte data1[12];

        byte addr0[8];
        byte addr1[8];
        
        if (!ds0.search(addr0)) 
        {
            ds0.reset_search();
            Serial.print("1");
            return;
        }
        
        if (!ds1.search(addr1)) 
        {
            ds1.reset_search();
            Serial.print("2");
            return;
        }

        if (OneWire::crc8(addr0, 7) != addr0[7])
        {
            Serial.print("3");
            return;
        }

        if (OneWire::crc8(addr1, 7) != addr1[7])
        {
            Serial.print("4");
            return;
        }
        
        ds0.reset();
        ds0.select(addr0);
        ds0.write(0x44, 1);

        ds0.reset();
        ds0.select(addr0);    
        ds0.write(0xBE);

        ds1.reset();
        ds1.select(addr1);
        ds1.write(0x44, 1);
        
        ds1.reset();
        ds1.select(addr1);    
        ds1.write(0xBE);
        
        for (int i = 0; i < 9; i++)
            data0[i] = ds0.read();

        for (int i = 0; i < 9; i++)
            data1[i] = ds1.read();
        
        int16_t raw0 = (data0[1] << 8) | data0[0];
        int16_t raw1 = (data1[1] << 8) | data1[0];
        
        switch (data0[4] & 0x60)
        {
            case 0x00:
                raw0 = raw0 & ~7;    // 9 bit resolution, 93.75 ms    
                break;

            case 0x20:
                raw0 = raw0 & ~3;    // 10 bit res, 187.5 ms
                break;

            case 0x40:
                raw0 = raw0 & ~1;    // 11 bit res, 375 ms
                break;
        }

        switch (data1[4] & 0x60)
        {
            case 0x00:
                raw1 = raw1 & ~7;    // 9 bit resolution, 93.75 ms    
                break;

            case 0x20:
                raw1 = raw1 & ~3;    // 10 bit res, 187.5 ms
                break;

            case 0x40:
                raw1 = raw1 & ~1;    // 11 bit res, 375 ms
                break;
        }
        
        uint8_t lsb0 = (raw0 & 0x3F) | 0xC0;
        uint8_t msb0 = (raw0 >> 6) & 0x3F;

        uint8_t lsb1 = (raw1 & 0x3F) | 0xC0;
        uint8_t msb1 = (raw1 >> 6) & 0x3F;
        
        //Serial.write(lsb0);
        //Serial.write(msb0);
        //Serial.write(lsb1);
        //Serial.write(msb1);
        
        Serial.print(raw0 / 16)
        Serial.print(raw1 / 16)

        t1 = t0;
    }
}
