save_today:
	source confluent-documentation-quality/bin/activate && python generate_data.py && python plot_data.py

publish:
	git add -A
	git commit -m "$(shell date) | daily data gathered"
	git push