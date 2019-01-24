MAIN_MAKE := $(abspath $(lastword $(MAKEFILE_LIST)))
TOP := $(patsubst %Makefile,%,$(THIS_MAKEFILE))
TINYUSB := lib/tinyusb
OUTPUT := output

BOARD := metro_m0_express
# Don't know what these are for yet
LD_FILE = $(TINYUSB)/hw/bsp/$(BOARD)/samd21g18a_flash.ld
LD_FLAGS += -mthumb -mcpu=cortex-m0plus

# Cflags copied from board.mk
CFLAGS = \
	-DCFG_TUSB_MCU=OPT_MCU_SAMD21 \
	-DCONF_DFLL_OVERWRITE_CALIBRATION=0 \
	-D__SAMD21G18A__ \
	-mthumb \
	-mabi=aapcs-linux \
	-mcpu=cortex-m0plus \
	-msoft-float \
	-mfloat-abi=soft

# SRC_C includes all c files that will be compiled	
SRC_C += \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/gcc/gcc/startup_samd21.c \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/gcc/system_samd21.c \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hpl/gclk/hpl_gclk.c \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hpl/pm/hpl_pm.c \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hpl/sysctrl/hpl_sysctrl.c
	
# INC includes all header files that will be included	
INC += \
	-I$(TOP)/$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/ \
	-I$(TOP)/$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/config \
	-I$(TOP)/$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/include \
	-I$(TOP)/$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hal/include \
	-I$(TOP)/$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hal/utils/include \
	-I$(TOP)/$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd51/hpl/pm/ \
	-I$(TOP)/$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hpl/port \
	-I$(TOP)/$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hri \
	-I$(TOP)/$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/CMSIS/Include

