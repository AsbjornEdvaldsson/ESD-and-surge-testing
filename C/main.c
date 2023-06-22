/*
 * File:   main.c
 * Author: ASB
 *
 * Created on February 27, 2023, 11:57 AM
 */

#define F_CPU 1000000 //8MHz default clock speed (does not define, only for delay)

#include <avr/io.h>
#include <util/delay.h>
#include <avr/pgmspace.h>

#define NUM_MEAS 4 //One less than actual since counting starts at 0

/*
 * num : number of measurement you want
 * a_b : 0 -> a, 1->b
 
 */
uint8_t Port_update(uint8_t num, uint8_t a_b){
    if(num > NUM_MEAS){
        return 0x00;
    }
    if(a_b > 1){
        return 0x00;
    }
    
    
    static const __flash uint8_t A_meas[NUM_MEAS+1] = {
        0x7, 
        0x7,
        0x7,
        0x3,
        0xf
    };
    
    
    static const __flash uint8_t B_meas[NUM_MEAS+1] = {
        0x3,
        0xf,
        0xb,
        0xb,
        0xb
    };
    
    //A PA0 trough PA3 are S2_0 trough S2_3 
    //PA7 is S1_3
    //Other PA pins are for ISP programming
    
    //PB0 : S1_0
    //PB1 : S1_1
    //PB2 : S1_2
    //PB3 : ISP programming
    
    //Change from above to correct pinout on ATtiny.
    uint8_t a = 0x00;
    uint8_t b = 0x00;
    
    a |= (0b00001111 & B_meas[num]) | (0b10000000 & (A_meas[num] << 4));
    b |= 0b00000111 & A_meas[num];
    
    if(a_b == 1) return b;
    else return a;
}

int main(void) {
    
    
    /*
     SET BIT n : x |= (1<<n);
     UNSET BIT n : x &= ~(1<<n);
     */
    
    //A PA0 trough PA3 are S2_0 trough S2_3 
    //PA7 is S1_3
    //Other PA pins are for ISP programming
    
    //PB0 : S1_0
    //PB1 : S1_1
    //PB2 : S1_2
    //PB3 : ISP programming
    
    
    
    //PORTA = Port A Data Register (1 set as high, 0 set as low)
    PORTA |= (1<<PA0);
    PORTA |= (1<<PA1);
    PORTA |= (1<<PA2);
    PORTA |= (1<<PA3);
    
    PORTB |= (1<<PB0);
    PORTB |= (1<<PB1);
    PORTB |= (1<<PB2);
    PORTA |= (1<<PA7);
    
    
    //DDRA = Port A Data Direction Register (0 is input, 1 is output)
    DDRA |= (1<<PA0);
    DDRA |= (1<<PA1);
    DDRA |= (1<<PA2);
    DDRA |= (1<<PA3);

    DDRB |= (1<<PB0);
    DDRB |= (1<<PB1);
    DDRB |= (1<<PB2);
    DDRA |= (1<<PA7);
    
    //Before DDRA the PORTA notes how the pullup is defined (See https://ww1.microchip.com/downloads/en/DeviceDoc/ATtiny24A-44A-84A-DataSheet-DS40002269A.pdf section 10.1.3)
    //but after the DDRA it is to write to the outputs
    
    
    DDRA &= ~(1 << PINA6);
    
    //PA6 is the push button
    
    //PINA = Port A Input Pins
    // i = PINA //Read input pins on Port A (stored as 0b????????)
    
    uint8_t i = 0;
    uint8_t flag = 0;
    
    PORTA = 0x00;
    PORTB = 0x00;
    
    while (1) {
        
        uint8_t pinValue = (PINA & (1 << PINA6)) >> PINA6;
        
        if(!pinValue && flag == 0){
            flag = 1;
        }
        
        if(flag == 1){
            //Toggle between the 32 measurement points one by one with a delay of 1sec
            PORTA = Port_update(i,0);
            PORTB = Port_update(i,1);
            _delay_ms(980);
            PORTA = 0x00;
            PORTB = 0x00;
            i += 1;
        }
        
        if(i > NUM_MEAS){
            i = 0;
            flag = 0;
        }
        _delay_ms(10);
    }
}
