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

# ---- merge
merge:
	$(call require_arg,merge)
	python3 generator/merge_realizations.py $(ARG)

# ---- split
split:
	$(call require_arg,split)
	python3 generator/split_realizations.py $(ARG)

# ---- build
build:
	$(call require_arg,build)
	python3 generator/generate_site_assets.py $(ARG)
	python3 generator/render_block.py $(ARG)



validate:
	@set -e; \
	for block in blocks/*; do \
		if [ -d "$$block/realization" ] && [ -f "$$block/schema.json" ]; then \
			echo "Validating $$block"; \
			for json in $$block/realization/*.json; do \
				if [ -f "$$json" ]; then \
					python generator/validate_json.py $$block/schema.json $$json; \
				fi; \
			done; \
		fi; \
	done; \
	echo "All realizations are valid"
clean:
	@echo "Removing non-test realization json files..."
	@rm -vf b_index.html site.css site.js
	@find blocks -type f -path "*/realization/*.json" \
        ! -name "test_*.json" \
        ! -name "default_*.json" \
        -delete

