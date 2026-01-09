

.PHONY: validate-realizations

validate-realizations:
	@set -e; \
	for block in blocks/*; do \
		if [ -d "$$block/realization" ] && [ -f "$$block/schema.json" ]; then \
			echo "🔍 Validating $$block"; \
			for json in $$block/realization/*.json; do \
				if [ -f "$$json" ]; then \
					python generator/validate_json.py $$block/schema.json $$json; \
				fi; \
			done; \
		fi; \
	done; \
	echo "✅ All realizations are valid"

