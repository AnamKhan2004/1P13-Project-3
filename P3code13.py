ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P3B' # Enter the project identifier i.e. P3A or P3B

# SERVO TABLE CONFIGURATION
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 90 # enter the value in degrees for the classification tower
drop_tube_angle = 180 # enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# BIN CONFIGURATION
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.13 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin1_metallic = False

bin2_offset = 0.13
bin2_color = [0,1,0]
bin2_metallic = False

bin3_offset = 0.13
bin3_color = [0,0,1]
bin3_metallic = False

bin4_offset = 0.13
bin4_color = [0,0,0]
bin4_metallic = False
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
if project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
else:
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color],[bin1_metallic,bin2_metallic, bin3_metallic,bin4_metallic]]
    configuration_information = [table_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bot = qbot(0.1,ip_address,QLabs,project_identifier,hardware)
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------
is_container_dispensed = False

def dispense_container(container_num):
    #dispensing a container using the number given in the parameters
    material, mass, bin_num = table.dispense_container(container_num, True)
    #returns the mass to be used by load container
    return mass


def check_bin_color(container_num):
    #returns the colour bin the container should go to
    if (container_num == 2) or (container_num == 5):
        bin_color = ([1, 0, 0], [255, 0, 0])
    elif container_num == 3:
        bin_color = ([0, 1, 0], [0, 255, 0])
    else:
        bin_color = ([0, 0, 1], [0, 0, 255])
    return bin_color


def load_container(mass):
    global current_pos
    print(current_pos)
    #checking conditions for container to be loaded
    if (mass < 90):

        home_pos = [0.406, 0.0, 0.483]
        can_pos = [0.635, 0.0, 0.24]
        dropoff_pos = [[0.017, -0.554, 0.54],[0.028, -0.48, 0.52],[0.007, -0.412, 0.49]]
        #Moves arm to the container, picks up container
        arm.move_arm(0.522, 0.0, 0.391)
        time.sleep(1)
        arm.move_arm(can_pos[0], can_pos[1], can_pos[2])
        time.sleep(1)
        arm.control_gripper(40)
        #Moves arm to dropoff location, drops container
        time.sleep(1)
        arm.move_arm(0.174, -0.0, 0.638)
        time.sleep(1)
        arm.rotate_base(-100)
        time.sleep(1)
        arm.move_arm(dropoff_pos[current_pos][0], dropoff_pos[current_pos][1], dropoff_pos[current_pos][2])
        time.sleep(2)
        arm.control_gripper(-40)
        time.sleep(1)
        arm.move_arm(0.0, -0.174, 0.638)
        time.sleep(1)
        current_pos += 1
        print(current_pos)

        

def line_following():
    #setting the bot's speed based on what the line sensors detect and allowing the bot to turn
    line_sensor = bot.line_following_sensors()
    if line_sensor[0] == 1 and line_sensor[1] == 1:
        bot.set_wheel_speed([0.03,0.03])
    elif line_sensor[0] == 1 and line_sensor[1] == 0:
        bot.set_wheel_speed([0.02,0.045])
    elif line_sensor[0] == 0 and line_sensor[1] == 1:
        bot.set_wheel_speed([0.045,0.02])
        
            
def transfer_container(container_num):
    bin_color = check_bin_color(container_num)
    bot.activate_line_following_sensor()
    bot.activate_color_sensor()
    #using a while loop to continuously check the colour sensors to see if it matches the target bin
    while True:
        color_sensed = bot.read_color_sensor()
        bot.line_following_sensors()
        if color_sensed == bin_color:
            time.sleep(1.5)
            #if the colour matches, the bot stops and breaks out of the while loop
            #adjusting the q bot to stop directly in front of the bin (depending on bin colour)
            if (bin_color == ([1, 0, 0], [255, 0, 0])) or (bin_color == ([0, 0, 1], [0, 0, 255])):
                if (container_num == 4) or (container_num == 6):
                    bot.stop()
                    bot.deactivate_color_sensor()
                    bot.deactivate_line_following_sensor()
                    bot.forward_time(9)
                else:
                    time.sleep(6.5)
                    bot.stop()
                    bot.deactivate_color_sensor()
                    bot.deactivate_line_following_sensor()
                    bot.forward_time(1)
            else:
                bot.stop()
                bot.deactivate_color_sensor()
                bot.deactivate_line_following_sensor()
                bot.forward_time(2.5)
            break
        #line following is called in the while loop so the bot continuously to move and turn
        line_following()
        
        

def deposit_container():
    #rotates the hopper to deposit containers, then rotates it back to the original position
    bot.activate_linear_actuator()
    time.sleep(2)
    bot.rotate_hopper(50)
    time.sleep(5)
    bot.rotate_hopper(0)
    bot.deactivate_linear_actuator()


def return_home():
    bot.activate_line_following_sensor()
    current_pos = bot.position()
    #using a while loop to continously check the bot's position
    while True:
        bot.line_following_sensors()
        current_pos = bot.position()
        #if the current position is within a range of positions close to starting position, the bot will stop
        if (1.25 <= current_pos[0] <= 2) and (-0.1 <= current_pos[1] <= 0.1) and (-0.1 <= current_pos[2] <= 0.1):
            time.sleep(3)
            bot.stop()
            bot.deactivate_line_following_sensor()
            break
        line_following()
    

def main():
    for i in range (3):
        global is_container_dispensed
        global current_pos
        current_pos = 0
        #initializing mass
        mass = 0
        container_num = [random.randint(1,6), random.randint(1,6), random.randint(1,6)] 

        #getting number of first container to check if next containers go to the same bin
        container_num_old = container_num[0]
        for i in range (3):
            #dispenses 3 containers

            if is_container_dispensed == True:
                table.rotate_table_angle(180)
                load_container(mass)
                is_container_dispensed = False
                break

            
            container_num_new = container_num[i]

            #gets mass from dispense container function
            mass_new = dispense_container(container_num_new)
            
            #checks drop off locations for first container loaded and current container
            bin_color_old = check_bin_color(container_num_old)
            bin_color_new = check_bin_color(container_num_new)
            
            #breaks out of the loop as to not dispense a new container if current container is not going to the same bin as previous container
            if bin_color_old != bin_color_new:
                table.rotate_table_angle(180)
                is_container_dispensed = True
                break

            #mass of new container is passed as a parameter to load container function to check conditions of mass
            mass += mass_new
            load_container(mass)
            time.sleep(2)
            time.sleep(4)
        
        time.sleep(2)
        transfer_container(container_num_old)
        deposit_container()
        return_home()

main()

#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

    

