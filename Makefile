.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "Available tasks:"
	@echo "    watch  Upload changed *.py files to /pyboard automatically"
	@echo "    shell  Start an remote shell session"
	@echo "    sync   Copy all *.py files to /pyboard"
	@echo "    reset  Soft reboot the board"
	@echo "    repl   Start a repl session"
	@echo ""

watch:
	find . -name "*.py" | entr -c sh -c 'make sync && make reset'

sync:
	rshell --port /dev/tty.SLAB_USBtoUART --timing --buffer-size=32 cp --recursive *.py /pyboard

shell:
	rshell --port /dev/tty.SLAB_USBtoUART --timing --buffer-size=32

repl:
	rshell --port /dev/tty.SLAB_USBtoUART --timing --buffer-size=32 repl

reset:
	rshell --port /dev/tty.SLAB_USBtoUART --timing --buffer-size=32 repl "~ import machine ~ machine.reset()~"

dist:
	python3 setup.py sdist

.PHONY: help watch shell repl reset sync dist
