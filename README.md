# poLoNodes
## USB Connection Map 


![polo_USB.JPG](https://github.com/mi3nts/poLoNodes/blob/main/Resources/Images/polo_USB.JPG)

> 1. WiFi Antenna
> 2. Canaree Sensor
> 3. LoRa WAN Board
> 4. 3-Split USB -> GPS, MIC, blank


## C4 Pinouts 


![c4_pinmap.png](https://github.com/mi3nts/poLoNodes/blob/main/Resources/Images/c4_pinmap.png)


## Wiring Map 

![Box_hole.JPG](https://github.com/mi3nts/poLoNodes/blob/main/Resources/Images/Box_hole.JPG)

> 1. GPS USB **IN** (*from 8*), DC Barrel Type Power **IN** (*from 5*)
> 2. LoRa Antenna Wire **OUT** (*from LoRa WAN Board*) 
> 3. MIC 3.5mm **IN** (*from 8*), I2C **IN** (*from SRS*)
> 4. Canaree USB **IN** (*from SRS*), USB wire for WiFi Antenna **OUT** (*from USB1*)
> 5. USB wire for WiFi Antenna **IN** (*from 4*),  DC Barrel Type Power **OUT** (*from adapter and switch*)
> 6. Switch
> 7. WiFi Antenna
> 8. GPS USB **IN & OUT** (*cable management*), MIC Wire **IN & OUT**, AC Power Cord **IN** (*cable management*)

## HOW TO READ DATA?

> 1. From MINTS Team member collect credential files.
> 2. Paste them in cloned git repository poLoNodes and in the following folder ```poLoNodes\firmware\xu4LoRa\mintsXU4\credentials```
> 3. Update the nodeID from DWServices for the particular node in the file ```poLoNodes\firmware\xu4LoRa\mintsXU4\credentials\nodeIDs.yaml```
> 4. Go to ```poLoNodes\firmware\xu4LoRa```
> 5. Install needed libraries.
> 6. Run  ```python3 r_1_loRaRecieve.py```
> 7. If running properly it should show data strings.

