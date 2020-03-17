#!/usr/bin/env bash
export IS_DEBUG=${DEBUG:-true}
exec gunicorn -w 8 --bind 0.0.0.0:5000 --access-logfile - --error-logfile - app:app