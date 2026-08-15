#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path('builder').resolve()))
from build_Android import AndroidDeploy

if __name__ == '__main__':
    AndroidDeploy(platform='aarch64', app_name='Learnly-Grade8', package_name='org.learnly.grade8', version='1.0.0', project_dir=Path.cwd()).deploy()
