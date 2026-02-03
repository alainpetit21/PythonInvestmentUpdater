cd /home/alain/Work/AlainPetit/Code/PythonInvestmentUpdater/
source .venv/bin/activate
export PYTHONPATH="/home/alain/Work/AlainPetit/Code/PythonInvestmentUpdater/Src"
python Src/main.py --xml "/home/alain/Documents/Alain Petit/Others/finances.xml" --input data/AlainRRSP.xlsx --config data/config.json --out "/home/alain/Documents/Alain Petit/Others/finances.xml"
python -m Src.main --xml "/home/alain/Documents/Alain Petit/Others/finances.xml" --input data/AlainTFSA.xlsx --config data/config.json --out "/home/alain/Documents/Alain Petit/Others/finances.xml"
python -m Src.main --xml "/home/alain/Documents/Alain Petit/Others/finances.xml" --input data/AraceliRRSP.xlsx --config data/config.json --out "/home/alain/Documents/Alain Petit/Others/finances.xml"
python -m Src.main --xml "/home/alain/Documents/Alain Petit/Others/finances.xml" --input data/AraceliTFSA.xlsx --config data/config.json --out "/home/alain/Documents/Alain Petit/Others/finances.xml"