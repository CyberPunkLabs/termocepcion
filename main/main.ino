#include <OneWire.h>


#define DUAL

uint16_t peltier0h = 18;
uint16_t peltier0c = 19;
uint16_t sensor0 = 13;

#ifdef DUAL
uint16_t peltier1h = 22;
uint16_t peltier1c = 23;
uint16_t sensor1 = 0;
#endif

uint8_t  resolution = 13;
double   frequency  = 10000;


OneWire ds(sensor0);

int t0;
int t1 = millis();


void setup(void) 
{
    Serial.begin(115200);

    ledcSetup(0, frequency, resolution);
    ledcAttachPin(peltier0h, 0);

    ledcSetup(1, frequency, resolution);
    ledcAttachPin(peltier0c, 1);

    #ifdef DUAL
    ledcSetup(2, frequency, resolution);
    ledcAttachPin(peltier1h, 0);

    ledcSetup(3, frequency, resolution);
    ledcAttachPin(peltier1c, 1);
    #endif
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
        
        uint32_t dutyCycle1 = ((static_cast<uint32_t>(packet[1]) & 0x3F) << 7) | (static_cast<uint32_t>(packet[0]) & 0x7F);
        bool polarity0 = packet[1] & 0x40;
        
        #ifdef DUAL
        uint32_t dutyCycle2 = ((static_cast<uint32_t>(packet[3]) & 0x3F) << 7) | (static_cast<uint32_t>(packet[2]) & 0x7F);
        bool polarity1 = packet[3] & 0x40;
        #endif

        if (polarity0)
        {
            ledcWrite(0, 0);
            ledcWrite(1, dutyCycle1);
        }
        else
        {
            ledcWrite(1, 0);
            ledcWrite(0, dutyCycle1);
        }
        
        #ifdef DUAL
        if (polarity1)
        {
            ledcWrite(2, 0);
            ledcWrite(3, dutyCycle2);
        }
        else
        {
            ledcWrite(3, 0);
            ledcWrite(2, dutyCycle2);
        }
        #endif
    }

    t0 = millis();

    if (t0 - t1 > 750)
    {
        byte data[12];
        byte addr[8];
        float celsius;

        if (!ds.search(addr)) 
        {
            ds.reset_search();
            return;
        }

        if (OneWire::crc8(addr, 7) != addr[7])
            return;

        ds.reset();
        ds.select(addr);
        ds.write(0x44, 1);

        ds.reset();
        ds.select(addr);    
        ds.write(0xBE);

        for (int i = 0; i < 9; i++)
            data[i] = ds.read();

        int16_t raw = (data[1] << 8) | data[0];

        switch (data[4] & 0x60)
        {
            case 0x00:
                raw = raw & ~7;    // 9 bit resolution, 93.75 ms    
                break;

            case 0x20:
                raw = raw & ~3;    // 10 bit res, 187.5 ms
                break;

            case 0x40:
                raw = raw & ~1;    // 11 bit res, 375 ms
                break;
        }

        uint8_t lsb = (raw & 0x3F) | 0xC0;
        uint8_t msb = (raw >> 6) & 0x3F;

        Serial.write(lsb);
        Serial.write(msb);
        Serial.write(0);
        Serial.write(0);

        t1 = t0;
    }
}
