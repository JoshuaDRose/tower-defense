venv/bin/activate: requirements.txt
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

run: venv/bin/activate
	./venv/bin/python3 src

build:
	pyinstaller src/__main__.py --onefile

clean:
	rm -rf src/__pycache__
	rm -rf venv
