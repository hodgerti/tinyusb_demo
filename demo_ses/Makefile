MAIN_MAKE := $(abspath $(lastword $(MAKEFILE_LIST)))
TOP := $(patsubst %Makefile,%,$(THIS_MAKEFILE))
TINYUSB := lib/tinyusb
OUTPUT := output

# Don't know what these are for yet
LD_FILE = $(TINYUSB)/hw/bsp/metro_m0_express/samd21g18a_flash.ld
LD_FLAGS += -mthumb -mcpu=cortex-m0plus

# Compiler variables
CROSS_COMPILE = arm-none-eabi-

CC = $(CROSS_COMPILE)gcc
CXX = $(CROSS_COMPILE)g++
LD = $(CROSS_COMPILE)ld
OBJCOPY = $(CROSS_COMPILE)objcopy
MKDIR = mkdir
SED = sed
CP = cp
RM = rm

# Board flags
CFLAGS = \
	-DCFG_TUSB_MCU=OPT_MCU_SAMD21 \
	-DCONF_DFLL_OVERWRITE_CALIBRATION=0 \
	-D__SAMD21G18A__ \
	-mthumb \
	-mabi=aapcs-linux \
	-mcpu=cortex-m0plus \
	-msoft-float \
	-mfloat-abi=soft \

# Project Flags
CFLAGS += \
	-fsingle-precision-constant \
	-fno-strict-aliasing \
	-Wdouble-promotion \
	-Wno-endif-labels \
	-Wstrict-prototypes \
	-Werror-implicit-function-declaration \
	-Wfloat-equal \
	-Wundef \
	-Wshadow \
	-Wwrite-strings \
	-Wsign-compare \
	-Wmissing-format-attribute \
	-Wno-deprecated-declarations \
	-Wnested-externs \
	-Wunreachable-code \
	-Wcast-align \
	-Wno-error=lto-type-mismatch \
	-ffunction-sections \
	-fdata-sections

# Board firmware sources
SRC_C += \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/gcc/gcc/startup_samd21.c \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/gcc/system_samd21.c \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hpl/gclk/hpl_gclk.c \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hpl/pm/hpl_pm.c \
	$(TINYUSB)/hw/mcu/microchip/samd/asf4/samd21/hpl/sysctrl/hpl_sysctrl.c
	
# tinyusb lib sources
SRC_C += \ 
	$(TINYUSB)/hw/bsp/metro_m0_express/board_metro_m0_express.c \
	$(TINYUSB)/src/common/tusb_fifo.c \
	$(TINYUSB)/src/device/usbd.c \
	$(TINYUSB)/src/device/usbd_auto_desc.c \
	$(TINYUSB)/src/device/usbd_control.c \
	$(TINYUSB)/src/class/msc/msc_device.c \
	$(TINYUSB)/src/class/cdc/cdc_device.c \
	$(TINYUSB)/src/class/hid/hid_device.c \
	$(TINYUSB)/src/tusb.c \
	$(TINYUSB)/src/portable/microchip/samd21/dcd_samd21.c
	
# Project sources
SRC_C += \ 
	src/main.c \
	src/msc_app.c \
	src/msc_disk_ram.c \
	src/tusb_descriptors.c

# Board firmware headers
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

# Project headers
INC += \
	-Isrc \
	-I$(TOP)/$(TINYUSB)/hw \
	-I$(TOP)/$(TINYUSB)/src

#Debugging/Optimization
ifeq ($(DEBUG), 1)
  CFLAGS += -O0 -ggdb
else
  CFLAGS += -flto -Os
endif

# Grouping together the build
CFLAGS += $(INC) -Wall -Werror -std=gnu11 -nostdlib -DBOARD_METRO_M0_EXPRESS
LDFLAGS += $(CFLAGS) -nostartfiles -fshort-enums -Wl,-T,$(TOP)/$(LD_FILE) -Wl,-Map=$@.map -Wl,-cref -Wl,-gc-sections -specs=nosys.specs -specs=nano.specs
LIBS := -lgcc -lc -lm -lnosys

OBJ = $(addprefix $(OUTPUT)/obj/, $(SRC_C:.c=.o))
OBJ += $(addprefix $(OUTPUT)/obj/, $(SRC_S:.s=.o))

all: $(OUTPUT)/metro_m0_express-firmware.bin

OBJ_DIRS = $(sort $(dir $(OBJ)))
$(OBJ): | $(OBJ_DIRS)
$(OBJ_DIRS):
	@$(MKDIR) -p $@
	
$(BUILD)/metro_m0_express-firmware.elf: $(OBJ)
	@echo LINK $@
	@$(CC) -o $@ $(LDFLAGS) $^ -Wl,--start-group $(LIBS) -Wl,--end-group
	
$(BUILD)/metro_m0_express-firmware.bin: $(BUILD)/metro_m0_express-firmware.elf
	@echo CREATE $@
	$(OBJCOPY) -O binary -j .vectors -j .text -j .data $^ $@
	
# We set vpath to point to the top of the tree so that the source files
# can be located. By following this scheme, it allows a single build rule
# to be used to compile all .c files.
vpath %.c . $(TOP)
$(BUILD)/obj/%.o: %.c
	@echo CC $@
	@$(CC) $(CFLAGS) -c -MD -o $@ $<
	@# The following fixes the dependency file.
	@# See http://make.paulandlesley.org/autodep.html for details.
	@# Regex adjusted from the above to play better with Windows paths, etc.
	@$(CP) $(@:.o=.d) $(@:.o=.P); \
	  $(SED) -e 's/#.*//' -e 's/^.*:  *//' -e 's/ *\\$$//' \
	      -e '/^$$/ d' -e 's/$$/ :/' < $(@:.o=.d) >> $(@:.o=.P); \
	  $(RM) $(@:.o=.d)

clean:
	rm -rf build-metro_m0_express