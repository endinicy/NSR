"""
This script is a basic Modbus RTU Slave simulator.

"""


import sys

import logging
import threading

import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus as modbus
import modbus_tk.modbus_rtu as modbus_rtu
import serial


# argparse documentation
import argparse

parser = argparse.ArgumentParser(description='Description: This script is a basic Modbus RTU Slave simulator which facilitates the running of a server of Modbus Slaves. Arguments listed below are initiation arguments, once the scrpt is running, there is a whole slew of different commands you can use to edit the Modbus Slave server in real-time. Type \`help\' in script to view the commands.')
parser.add_argument('--slaves_init', type=float,
                    help='The file name of a CSV file containing slave server info. I hope there is an example file somewhere to reference.')
args = parser.parse_args()

if args.slaves_init != None:
    print('The slave initialization function is not yet supported\n')



logger = modbus_tk.utils.create_logger(name="console", record_format="%(message)s")

if __name__ == "__main__":
    portName = '/dev/tty.SLAB_USBtoUART'
    baudrate = 11520
    #Create the server
    server = modbus_rtu.RtuServer(serial.Serial(port=portName, baudrate=baudrate))

    server_hist={}
    try:
        logger.info("running...")
        logger.info("enter 'quit' to close the server or 'help' to view available commands")
         
        server.start()
#    
#        slave_1 = server.add_slave(1)
#        slave_1.add_block('0', cst.HOLDING_REGISTERS, 100, 100)
        
        while True:
            cmd = sys.stdin.readline()
            args = cmd.split(' ')
            if cmd.find('quit')==0:
                sys.stdout.write('bye-bye\r\n')
                break
            elif cmd.find('help')==0:
                sys.stdout.write('\n\nWorry not, HELP TEXT IS HERE!\r\nAvailable commands: (no brackets, all args separated by spaces)\r\n\n')
                sys.stdout.write('add_slave [slave_id ]\r\n')
                sys.stdout.write('add_block [slave_id block_name block_type starting_address block_length ]\r\n')
                sys.stdout.write('set_values [slave_id block_name reg_address value(s) ]\r\n')
                sys.stdout.write('get_values [slave_id block_name starting_address length ]\r\n\n')

            elif cmd.find('status')==0:
                sys.stdout.write(str(server_hist))
                sys.stdout.write('\n')

            elif args[0]=='add_slave':
                try:
                    slave_id = int(args[1])
                    server.add_slave(slave_id)
                    sys.stdout.write('done: slave %d added\r\n' % (slave_id))
                    server_hist[slave_id]={}
                    if slave_id not in server_hist:
                        server_hist[slave_id]={}
                except:
                    sys.stdout.write('Error\n')
                    sys.stdout.write('Correct Syntax: add_slave [slave_id ]\r\n')
                    sys.stdout.write('Correct Usage: adds a new slave device with ID \'slave_id\'\n')

            elif args[0]=='add_block':
                try:
                    slave_id = int(args[1])
                    name = args[2]
                    block_type = int(args[3])
                    starting_address = int(args[4])
                    length = int(args[5])
                    slave = server.get_slave(slave_id)
                    slave.add_block(name, block_type, starting_address, length)
                    sys.stdout.write('done: block %s added\r\n' % (name))
                    if name not in server_hist[slave_id]:
                        server_hist[slave_id][name]={}
                        server_hist[slave_id][name]['type']=block_type

                except:
                    sys.stdout.write('Error\n')
                    sys.stdout.write('Correct Syntax: add_block [slave_id block_name block_type starting_address block_length ]\r\n')
                    sys.stdout.write('Correct Usage: adds a block named \'block_name\' at starting address \'starting_address\' of length \'block_length\' on slave with ID \'slave_id\'\r\n')
                    sys.stdout.write('Note: block types\n')
                    sys.stdout.write('      0: Coil              [Boolean, Master R/W]\n')
                    sys.stdout.write('      1: Discrete Inputs   [Boolean, Master Read Only]\n')
                    sys.stdout.write('      3: Input Registers   [Unsigned Word, Master R/W]\n')
                    sys.stdout.write('      4: Holding Registers [Unsigned Word, Read Only]\n')
            elif args[0]=='set_values':
                try:
                    slave_id = int(args[1])
                    name = args[2]
                    address = int(args[3])
                    values = []
                    for v in args[4:]:
                        values.append(int(v))
                    slave = server.get_slave(slave_id)
                    slave.set_values(name, address, values)
                    values = slave.get_values(name, address, len(values))
                    sys.stdout.write('done: values written: %s\r\n' % (str(values)))
                    valnum=0
                    for add in range(address,address+len(values)):
    #                    server_hist[slave_id][name][add]={}
                        server_hist[slave_id][name][add]=values[valnum]
                        valnum=valnum+1
                except:
                    sys.stdout.write('Error\n')
                    sys.stdout.write('Correct Syntax: set_values [slave_id block_name reg_address value(s) ]\r\n')
                    sys.stdout.write('Correct Usage: sets values for register \'reg_address\' on block  \'block name\' for slave with ID \'slave_id\'\n   Note: Multiple values can be written to successive addresses by entering multiple arguments for \'value(s)\'\r\n')
            elif args[0]=='get_values':
                try:
                    slave_id = int(args[1])
                    name = args[2]
                    address = int(args[3])
                    length = int(args[4])
                    slave = server.get_slave(slave_id)
                    values = slave.get_values(name, address, length)
                    sys.stdout.write('done: values read: %s\r\n' % (str(values)))
                except:
                    sys.stdout.write('Error\n')
                    sys.stdout.write('Correct Syntax: get_values [slave_id block_name starting_address length ]\r\n')
                    sys.stdout.write('Correct Usage: returns existing values of register \'reg_address\' on block  \'block name\' for slave with ID \'slave_id\'\n   Note: A \'length\' argument > 1 will return values for successive registers \n')
            else:
                sys.stdout.write("Unknown Command %s\r\n" % (args[0]))
    finally:
        server.stop()