# OPC UA Polling Client
# Keenan Granland
import asyncio
from asyncua import Client, Node, ua
import logging
from turtle import delay
import time

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

async def main(): 
    ## OPCUA INPUTS
    urlOPCUA = 'oct.tpc://172.31.1.236:4840/server/' #OPC UA Server Endpoint
    
    ## Initalise Variables
    Rd_Joi1 = 0.0
    S_reset = True  # State Tracking for Resetting Signals
    
    async with Client(url=urlOPCUA) as client:
        ## Initalise OPCUA Variables    
        # Create the NODE for each relevant variables
        # Use the namespace string here, can be found in UA Expert
        NODE_Rc_ProgID = client.get_node('ns=13;s=R1c_ProgID')
        NODE_Rc_Start = client.get_node('ns=13;s=R1c_Start;')
        NODE_Rf_Ready = client.get_node('ns=13;s=R1f_Ready;')
        NODE_Rd_Joi1 = client.get_node('ns=13;s=R1d_Joi1;')
        # add anyother OPC UA variables here
        
        ## Initalisation Routine
        # Add any intialisation functions here, 
        # For example homing a printer 
        
        print("Entering Main Polling Loop")
        while True: # Main Loop
            # Adjust the frequency of the polling
            await asyncio.sleep(0.2) 
            
            ## Read Control Variables
            Pc_Start = await NODE_Pc_Start.get_value() 
            Pc_ProgID = await NODE_Pc_ProgID.get_value() 
            
            ## Update Passive Variables
            # Example
            # Add code for reading Robot Joint 1 value
            # Then output Joint 1 data
            await NODE_Rd_Joi1.set_value(Rd_Joi1,ua.VariantType.Double) 
            
            
            #### Main Program ####
            if (Rc_Start==True)and(S_reset==False): #Main Program Selector
                # Set Ready Flag to false as program is running
                await NODE_Rf_Ready.set_value(Ready,ua.VariantType.Boolean)
                S_reset=True # Reset flag set to true
                
                ## Program 0 - Empty ##
                if (Pc_ProgID==0):
                    print('Program 0: Empty')
                    # Keep program 0 empty as it is the defult prog ID

                ## Program 1 ##
                elif (Pc_ProgID==1):#Add extra conditions for starting if needed
                    print('Program 1: ...')
                    # Add Code for operating the system here
                
                ## Program 2 ##                
                elif (Pc_ProgID==2):#Add programs with different functions 
                    print('Program 2: ...')
                
            ## Reset flag handler
            # Prevents infinite looping of the same program until 
            # Start flag has returned to 0
            if (Pc_Start==False)and(S_reset==True): 
                print('Wating for new Program Start')
                S_reset=False
                await NODE_Rf_Ready.set_value(True,ua.VariantType.Boolean) 
                
if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
