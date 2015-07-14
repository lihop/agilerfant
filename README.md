**Note:** This is a work in progress.

Requirements:
-------------
- python3.
- [requests](http://docs.python-requests.org/en/latest/) python http library.


Usage:
------
```
python3 agilerfant.py --help
```

Setting up git hooks:
---------------------
1. Add your usename password and backlog to the `credentials` file and copy it to the `.git/hooks/` directory in your repo.
2. Copy `prepare-commit-msg` to `.git/hooks/`. Uncomment the `STORY_NAME` setter appropriate for your branch naming scheme.
   Edit the shebang to point to your bash binary.
3. Copy `agilerfant.py` to `.git/hooks/`. Edit the shebang to point to your python3 binary. Note that this script requires
   the [requests](http://docs.python-requests.org/en/latest/) python library.

