#!/bin/bash
2	pylint back-end-python/gameactions/app.py
3	pytest back-end-python/tests/unit --cov-report=html --cov=gameactions --cov-branch
