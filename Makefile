.PHONY: merge split build consular_ua visa_ru visa_en

# ---- допустимі "параметри" (для tab-complete)
consular_ua:
	@:

auto_registration_ua:
	@:


visa_ru:
	@:

visa_en:
	@:

# ---- внутрішня змінна: другий аргумент
ARG := $(word 2, $(MAKECMDGOALS))

# ---- валідація аргументу
define require_arg
	@if [ -z "$(ARG)" ]; then \
		echo "ERROR: missing argument. Example: make $(1) consular_ua"; \
		exit 1; \
	fi
endef

merge:
	$(call require_arg,merge)
	python3 generator/cli.py merge $(ARG)

split:
	$(call require_arg,split)
	python3 generator/cli.py split $(ARG)

build:
	$(call require_arg,build)
	python3 generator/cli.py build $(ARG)

clean:
	$(call require_arg,clean)
	python3 generator/cli.py clean $(ARG)

validate:
	python3 generator/cli.py validate
