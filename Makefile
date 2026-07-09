# Makefile for Tools

CC = $(CROSS_COMPILE)g++

CFLAGS += -Wall -Wextra -O2

all: lpcisp lpcprog lpc_binary_check


OBJDIR = objs
SRC = $(shell find . -name \*.cpp)
OBJS = ${SRC:%.cpp=${OBJDIR}/%.o}

LPCISP_OBJS = ${OBJDIR}/lpcisp.o \
		${OBJDIR}/isp_utils.o \
		${OBJDIR}/isp_commands.o \
		${OBJDIR}/isp_wrapper.o \
		${OBJDIR}/serialib.o
	
LPCPROG_OBJS = ${OBJDIR}/lpcprog.o \
		${OBJDIR}/isp_utils.o \
		${OBJDIR}/isp_commands.o \
		${OBJDIR}/prog_commands.o \
		${OBJDIR}/parts.o \
		${OBJDIR}/serialib.o

LPCCHECK_OBJS = ${OBJDIR}/check.o \
		${OBJDIR}/isp_utils.o \
		${OBJDIR}/serialib.o

lpcisp: $(LPCISP_OBJS)
	@echo "Linking $@ ..."
	@$(CC) $(LDFLAGS) $(LPCISP_OBJS) -o $@
	@echo Done.

lpcprog: $(LPCPROG_OBJS)
	@echo "Linking $@ ..."
	@$(CC) $(LDFLAGS) $(LPCPROG_OBJS) -o $@
	@echo Done.

lpc_binary_check: $(LPCCHECK_OBJS)
	@echo "Linking $@ ..."
	@$(CC) $(LDFLAGS) $(LPCCHECK_OBJS) -o $@
	@echo Done.

${OBJDIR}/%.o: %.cpp
	@mkdir -p $(dir $@)
	@echo "-- compiling" $<
	@$(CC) -MMD -MP -MF ${OBJDIR}/$*.d $(CPPFLAGS) $(CFLAGS) $< -c -o $@


clean:
	rm -f ${OBJDIR}/*
mrproper: clean
	rm -f lpcisp
	rm -f lpcprog
	rm -f lpc_binary_check
	rm -f lpcisp.exe
	rm -f lpcprog.exe
	rm -f lpc_binary_check.exe