from django.test import TestCase
import re
import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'player.settings')
django.setup()
