//wattmeter codes start with 100
const uint16_t  E_WM_NotReady = 100;  //Wattmeter A/D returned status bit Not Ready
const uint16_t  E_WM_OutOfRange = 110;  //Wattmeter A/D returned status for invalid channel 
                                      //or over/under range on a valid channel
const uint16_t  E_WM_BadID = 120;  //Wattmeter A/D returned invalid chip ID number
const uint16_t  E_WM_BadPlus5 = 130;  //Wattmeter +5V power supply out of spec
const uint16_t  E_WM_BadMinus5 = 131;  //Wattmeter -5V power supply out of spec
const uint16_t  E_WM_BadRef = 132;  //Wattmeter 2.5V reference out of spec
const uint16_t  E_SlaveAck1 = 140;   //Didn't get a Slave Acknowledge from Pot for address
const uint16_t  E_SlaveAck2 = 141;   //Didn't get a Slave Acknowledge from Pot for value

//controller codes start with 200
const uint16_t  E_C_NoXDR = 200;  //Transducer is not connected
const uint16_t  E_C_FRAM = 210;  //Nonvolatile memeory checksum failed
const uint16_t  E_C_FLASH = 211;  //Program memory checksum failed
const uint16_t  E_C_RAM = 212;  //internal ram test failed
const uint16_t  E_C_BadPlus3V3 = 230;  //Controller +3.3V power supply out of spec
const uint16_t  E_C_BadPlus5 = 231;  //Controller +5V power supply out of spec
const uint16_t  E_C_BadPlus12 = 232;  //Controller +12V power supply out of spec
const uint16_t  E_C_DisplayCommand = 240;  //Display did not recognize the command
const uint16_t  E_C_DisplayBusy = 241;  //Display is busy
const uint16_t  E_C_DisplayStuck = 242;  //Display command pointer is not advancing
const uint16_t  E_C_TemperatureHigh = 243;  //Heatsink temperature is above 70 degrees C
const uint16_t  E_C_TemperatureLow = 244;  //probably open thermistor.
const uint16_t  E_C_NoPWRTable_A = 251;  //Couldn't find XDR_CHA.csv in SD card
const uint16_t  E_C_PWRChkSum_A  = 261;  //Checksum for XDR_CHA.csv failed
const uint16_t  E_C_NoPWRTable_B = 252;  //Couldn't find XDR_CHB.csv in SD card
const uint16_t  E_C_PWRChkSum_B  = 262;  //Checksum for XDR_CHB.csv failed
const uint16_t  E_C_NoPWRTable_C = 253;  //Couldn't find XDR_CHC.csv in SD card
const uint16_t  E_C_PWRChkSum_C  = 263;  //Checksum for XDR_CHC.csv failed
const uint16_t  E_C_NoPWRTable_D = 254;  //Couldn't find XDR_CHD.csv in SD card
const uint16_t  E_C_PWRChkSum_D  = 264;  //Checksum for XDR_CHD.csv failed
const uint16_t  E_C_SerialMis = 270; //SNs from serial port and power table don't match

//signal generator and phase detector codes start with 300
const uint16_t  E_SG_BadGen1 = 301;  //Channel A Signal Output is too low
const uint16_t  E_SG_BadPhase1 = 311;  //Channel B/C Phase Detector output is too high
const uint16_t  E_SG_BadGen2 = 302;  //Channel B Signal Output is too low
const uint16_t  E_SG_BadPhase2 = 312;  //Channel C/D Phase Detector output is too high
const uint16_t  E_SG_BadGen3 = 303;  //Channel B Signal Output is too low
const uint16_t  E_SG_BadPhase3 = 313;  //Channel C/D Phase Detector output is too high
const uint16_t  E_SG_BadGen4 = 304;  //Channel B Signal Output is too low
const uint16_t  E_SG_BadPhase4 = 314;  //Channel C/D Phase Detector output is too high
const uint16_t  E_SG_NotCoherent = 320;  //Coherent operation requested but not achieved
const uint16_t  E_SG_Coherent = 321;  //Incoherent operation requested but not achieved

//power output related errors start with 400
const uint16_t  E_P_HiDrive1 = 401;  //Channel A is taking too much drive
const uint16_t  E_P_Above1 = 411;    //Channel A is requiring above average drive
const uint16_t  E_P_Below1 = 421;    //Channel A is requiring below average drive
const uint16_t  E_P_LowDrive1 = 431; //Channel A is taking too little drive
const uint16_t  E_P_HiDrive2 = 402;  //Channel B is taking too much drive
const uint16_t  E_P_Above2 = 412;    //Channel B is requiring above average drive
const uint16_t  E_P_Below2 = 422;    //Channel B is requiring below average drive
const uint16_t  E_P_LowDrive2 = 432; //Channel B is taking too little drive
const uint16_t  E_P_HiDrive3 = 403;  //Channel C is taking too much drive
const uint16_t  E_P_Above3 = 413;    //Channel C is requiring above average drive
const uint16_t  E_P_Below3 = 423;    //Channel C is requiring below average drive
const uint16_t  E_P_LowDrive3 = 433; //Channel C is taking too little drive
const uint16_t  E_P_HiDrive4 = 404;  //Channel D is taking too much drive
const uint16_t  E_P_Above4 = 414;    //Channel D is requiring above average drive
const uint16_t  E_P_Below4 = 424;    //Channel D is requiring below average drive
const uint16_t  E_P_LowDrive4 = 434; //Channel D is taking too little drive
const uint16_t  E_P_HiEnergy  = 440;  //Total acoustic energy is over by 5%
const uint16_t  E_P_ChaPWR90A = 451;  //Channel A power over 90% or 7.5W safety margin
const uint16_t  E_P_ChaPWR30A = 461;  //Channel A power over 30% safety margin
const uint16_t  E_P_ChaPWR10A = 471;  //Channel A power outside 10% or 0.75W safety margin
const uint16_t  E_P_ChaPWR90B = 452;  //Channel B power over 90% or 7.5W safety margin
const uint16_t  E_P_ChaPWR30B = 462;  //Channel B power over 30% safety margin
const uint16_t  E_P_ChaPWR10B = 472;  //Channel B power outside 10% or 0.75W safety margin
const uint16_t  E_P_ChaPWR90C = 453;  //Channel C power over 90% or 7.5W safety margin
const uint16_t  E_P_ChaPWR30C = 463;  //Channel C power over 30% safety margin
const uint16_t  E_P_ChaPWR10C = 473;  //Channel C power outside 10% or 0.75W safety margin
const uint16_t  E_P_ChaPWR90D = 454;  //Channel D power over 90% or 7.5W safety margin
const uint16_t  E_P_ChaPWR30D = 464;  //Channel D power over 30% safety margin
const uint16_t  E_P_ChaPWR10D = 474;  //Channel D power outside 10% or 0.75W safety margin
const uint16_t  E_P_REVPWRA = 481;    //Channel A reverse power over 0.5W
const uint16_t  E_P_REVPWRB = 482;    //Channel B reverse power over 0.5W
const uint16_t  E_P_REVPWRC = 483;    //Channel C reverse power over 0.5W
const uint16_t  E_P_REVPWRD = 484;    //Channel D reverse power over 0.5W
const uint16_t  E_P_PWRSet = 490;     //PowerIndex variable set too low (<5W Electrical)
