import os

from git_helpers import get_guid




def main():
    guid = get_guid(skip_sanity_checks=True)
    with open(os.path.join(os.path.dirname(__file__), '..', 'commit.py'), 'w') as f:
        f.write("LAST_COMMIT_GUID = '{0}'\n".format(guid))

if __name__ == '__main__':
    main()
