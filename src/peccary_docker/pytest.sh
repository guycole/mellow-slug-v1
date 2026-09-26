#
# Title: pytest.sh
# Description: invoke pytest for loader
#
source venv/bin/activate
PYTHONPATH=$(pwd)/..; export PYTHONPATH
python -m pytest -q test_loader.py test_slug_app.py
#
