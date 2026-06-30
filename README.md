# Goofy Ahh password system
password system that inputs password using a ps4 controller. Plays a sound if the password is wrong (in your headphones), and will turn on a fan if the password is correct. Password inputs are managed on an Arduino Uno, and lock status of the fan can be seen there. 


The password so far is X S T C (X, Square, Triangle, Circle) buttons on the ps4 controller, also can be directly input from the serial monitor, in that case the python script is not necessary.
L1 to enter the password, R1 to relock the fan.

"error.wav" is the SYFM scene taken from the movie Bronson. All credits to them.

components used for hardware:
ps4 controller, potentiometer and 16x2 LCD, DC Fan and 9V2A battery, 1 manual switch to turn fan off manually, Arduino Uno, Jumper wires and breaboard for connections.

ill be giving the wiring diagram soon. Stay tuned


Also, the python script contains two parts: debug = true and debug = false. If you face any problems with the ps4 controller, use debug = true for troubleshooting, and set debug = false for the actual work
