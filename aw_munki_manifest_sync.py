#!/usr/bin/env python

import plistlib
import os
import sys
import argparse
import copy
import pprint
try:
    from pathlib import Path
except (ImportError, AttributeError):
    from pathlib2 import Path

# Load configuration file
from aw_config import *

from PyVMwareAirWatch.pyairwatch.client import AirWatchAPI
from PyVMwareAirWatch.pyairwatch.client import AirWatchAPIError

# For Python 2 compatibility
__metaclass__ = type

# Helper functions

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def log(level, message, ):
    '''Message logger, prints to stdout/stderr.'''
    if level == 'Error':
        eprint("{}: {}".format(level, message))
    elif level == 'Debug' and SCRIPT_VERBOSITY == True:
        print("{}: {}".format(level, message))
    else:
        print("{}: {}".format(level, message))

# Classes - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class Manifest():
    """Generic manifest superclass"""

    def __init__(self):
        self.definer = ''
        self.data = None
        self.default_data = None
        self.absolute_path = None
        self.relative_path = None
        self.changed = False

    def save(self):
        """Dumps manifest data to the file"""

        log('INFO', "Saving manifest {} to disk".format(self.relative_path))
        if sys.version_info[0] == 2:
            # Deprecated function. For Python 2.X only
            plistlib.writePlist(self.data.as_posix(), self.absolute_path)
        else:
            with self.absolute_path.open('wb') as file:
                plistlib.dump(self.data, file)

    def load(self):
        """Loads data from the manifest file"""

        if self.absolute_path.is_file():
            log('DEBUG', "Loaded manifest {} from disk".format(self.relative_path))
            if sys.version_info[0] == 2:
                # Deprecated function. For Python 2.X only
                self.data = plistlib.readPlist(self.absolute_path.as_posix())
            else:
                with self.absolute_path.open('rb') as file:
                    self.data = plistlib.load(file)
        else:
            log('DEBUG', "Initialized manifest {} with default data".format(self.relative_path))
            self.data = self.default_data
            self.changed = True

    def add_included(self, manifests, definer='', relative_dir=''):
        """Adds nested manifest. Ensures uniquness if necessary"""

        if not 'included_manifests' in self.data:
            self.data['included_manifests'] = []
            self.changed = True

        relative_paths = []

        for item in manifests:
            relative_paths.append(Path(relative_dir, definer + item).as_posix())
            if relative_paths[-1] not in self.data['included_manifests']:
                log('INFO', "Adding nested manifest {} to {}".format(relative_paths[-1], self.relative_path))
                self.data['included_manifests'].append(relative_paths[-1])
                self.changed = True

        if definer:
            for item in list(self.data['included_manifests']):
                if definer in item and item not in relative_paths:
                    log('INFO', "Removing nested manifest {} to {}".format(item, self.relative_path))
                    self.data['included_manifests'].remove(item)
                    self.changed = True

class DeviceManifest(Manifest):
    """Device manifest subclass"""

    def __init__(self, name):
        super(DeviceManifest, self).__init__()
        self.name = name
        self.relative_path = Path(MANIFEST_DEVICE_DIR, self.name).as_posix()
        self.absolute_path = Path(MANIFEST_DIR, MANIFEST_DEVICE_DIR, self.name)
        self.default_data = copy.deepcopy(DEFAULT_DEVICE_MANIFEST)
        super(DeviceManifest, self).load()

class UserManifest(Manifest):
    """User manifest subclass"""

    definer = 'airwatch_user_'

    def __init__(self, name):
        super(UserManifest, self).__init__()
        self.definer = UserManifest.definer
        self.name = self.definer + name
        self.relative_path = Path(MANIFEST_USER_DIR, self.name).as_posix()
        self.absolute_path = Path(MANIFEST_DIR, MANIFEST_USER_DIR, self.name)
        self.default_data = {}
        super(UserManifest, self).load()

class SmartgroupManifest(Manifest):
    """Smartgroup manifest subclass"""

    definer = 'airwatch_smartgroup_'

    def __init__(self, name):
        super(SmartgroupManifest, self).__init__()
        self.definer = SmartgroupManifest.definer
        self.name = self.definer + name
        self.relative_path = Path(MANIFEST_SMARTGROUP_DIR, self.name).as_posix()
        self.absolute_path = Path(MANIFEST_DIR, MANIFEST_SMARTGROUP_DIR, self.name)
        self.default_data = {}
        super(SmartgroupManifest, self).load()

class UsergroupManifest(Manifest):
    """Usergroup manifest subclass"""

    definer = 'airwatch_usergroup_'

    def __init__(self, name):
        super(UsergroupManifest, self).__init__()
        self.definer = UsergroupManifest.definer
        self.name = self.definer + name
        self.relative_path = Path(MANIFEST_USERGROUP_DIR, self.name).as_posix()
        self.absolute_path = Path(MANIFEST_DIR, MANIFEST_USERGROUP_DIR, self.name)
        self.default_data = {}
        super(UsergroupManifest, self).load()

# Manifest handlers (manifest logic) - - - - - - - - - - - - - - - - - - - - - - - - - - -

def handle_device_manifest(device):
    """Creates device manifest and updates nested user manifest if necessary"""

    device_manifest = DeviceManifest(device['serial'])

    # Ensure user manifest is assigned
    if 'user' in device:
        device_manifest.add_included([device['user']['name']],
                                     definer=UserManifest.definer,
                                     relative_dir=MANIFEST_USER_DIR)

    # Ensure smartgroup manifests are assigned
    device_manifest.add_included(device['smartgroups'],
                                 definer=SmartgroupManifest.definer,
                                 relative_dir=MANIFEST_SMARTGROUP_DIR)

    if device_manifest.changed:
        device_manifest.save()

def handle_device_manifests(devices):
    """Iterates over multiple device manifests and handles them"""

    for device in devices.values():
        handle_device_manifest(device)

def handle_user_manifests(users):
    """Creates user manifest and updates nested usergroup manifests if necessary"""

    for name, user in users.items():
        user_manifest = UserManifest(name)
        # Add nested if necessary and ensure old group are no longer present
        if 'groups' in user:
            user_manifest.add_included(user['groups'],
                                       definer=UsergroupManifest.definer,
                                       relative_dir=MANIFEST_USERGROUP_DIR)
        if user_manifest.changed:
            user_manifest.save()

def handle_smartgroup_manifests(smartgroups):
    """Creates smartgroup manifests"""
    for name in smartgroups.keys():
        smartgroup_manifest = SmartgroupManifest(name)
        if smartgroup_manifest.changed:
            smartgroup_manifest.save()

def handle_usergroup_manifests(groups):
    """Creates usergroup manifests"""
    for name in groups.keys():
        usergroup_manifest = UsergroupManifest(name)
        if usergroup_manifest.changed:
            usergroup_manifest.save()

# Extracting information from obtained JSON - - - - - - - - - - - - - - - - - - - - - - -

def extract_users(rawusers):
    """Constructs user data structure from AirWatch response"""

    users = {}
    for ruser in rawusers['Users']:
        if 'UserName' in ruser:
            name = ruser['UserName']
            if name not in AIRWATCH_USERS_IGNORE:
                users[name] = {'name': name, 'groups': []}
    return users

def extract_smartgroups(rawsmartgroups):
    """Constructs smartgroups data structure from AirWatch response"""
    smartgroups = {}
    for rsmartgroup in rawsmartgroups['SmartGroups']:
        if 'Name' in rsmartgroup:
            name = rsmartgroup['Name']
            if AIRWATCH_ALL_SMARTGROUPS or rsmartgroup['Name'] in AIRWATCH_SMARTGROUPS:
                smartgroups[name] = {}
                smartgroups[name]['name'] = name
                smartgroups[name]['id'] = rsmartgroup['SmartGroupID']
    return smartgroups


def extract_groups(rawgroups):
    """Constructs usergroup data structure from AirWatch response"""

    groups = {}
    for rgroup in rawgroups['ResultSet']:
        if 'groupName' in rgroup:
            name = rgroup['groupName']
            if AIRWATCH_ALL_USERGROUPS or rgroup['groupName'] in AIRWATCH_USERGROUPS:
                groups[name] = {}
                groups[name]['name'] = name
                groups[name]['id'] = rgroup['id']
                groups[name]['type'] = rgroup['type']

    return groups

def extract_devices(rawdevices):
    """Constructs device data structure from AirWatch response"""

    devices = {}
    for rdevice in rawdevices['Devices']:
        if 'SerialNumber' in rdevice:
            id = str(rdevice['Id']['Value'])
            devices[id] = {}
            devices[id]['serial'] = rdevice['SerialNumber']
            devices[id]['id'] = id
            devices[id]['smartgroups'] = []

            if rdevice['UserName'] and rdevice['UserName'] not in AIRWATCH_USERS_IGNORE:
                devices[id]['user'] = rdevice['UserName']

    return devices

def assign_groups(users, group, members):
    """Links user and groups data structures"""

    for member in members:
        if member['UserName'] in users:
            users[member['UserName']]['groups'].append(group['name'])
        else:
            print('Unknown user: {} in group {}'.format(member['UserName'], group['name']))
            exit(1)

def assign_smartgroups(devices, smartgroup, smartmembers, single_device=False):
    """Links device and smartgroups data structures"""

    for smartmember in smartmembers:
        if smartmember['Platform'] != AIRWATCH_MAC_PLATFORM:
            continue
        elif smartmember['Id'] in devices:
            devices[smartmember['Id']]['smartgroups'].append(smartgroup['name'])
        else:
            if not single_device:
                print('Unknown device: {} in smartgroup {}'.format(smartmember['Id'], smartgroup['name']))
                exit(1)

def assign_user(users, devices):
    """Links users and devices data structures"""

    for device in devices.values():
        if 'user' in device and device['user'] in users:
            device['user'] = users[device['user']]

# Query API a get necessary information  - - - - - - - - - - - - - - - - - - - - - - - - -

def sync_all_devicec(api):
    """Syncs all manifests"""

    # Get all AirWatch users
    rawusers = api.users.search()
    users = extract_users(rawusers)

    # Get desired AirWatch groups
    rawgroups = api.usergroups.search()
    groups = extract_groups(rawgroups)

    # Get desired group memberships
    for group in groups.values():
        rawmembers = api.usergroups.search_users(id=group['id'])
        if isinstance(rawmembers, dict):
            members = rawmembers['EnrollmentUser']
            # Assign groups to users
            log('DEBUG', 'Assigning groups to users')
            assign_groups(users, group, members)

    # Get all macOS devices
    rawdevices = api.devices.search_all(platform=AIRWATCH_MAC_PLATFORM)
    devices = extract_devices(rawdevices)

    # Assign users to devices
    assign_user(users, devices)

    # Get desired AirWatch smartgroups
    rawsmartgroups = api.smartgroups.search()
    smartgroups = extract_smartgroups(rawsmartgroups)

    # Get desired smartgroup memberships
    for smartgroup in smartgroups.values():
        rawsmartmembers = api.smartgroups.get_devices(id=smartgroup['id'])
        if isinstance(rawsmartmembers, dict):
            smartmembers = rawsmartmembers['Devices']
            # Assign smartgroups to devices
            log('DEBUG', 'Assigning smartgroups to devices')
            assign_smartgroups(devices, smartgroup, smartmembers)

    # 1. Ensure usergroup manifests exists
    log('DEBUG', 'Processing usergroup manifests')
    handle_usergroup_manifests(groups)

    # 2. Ensure user manifests exists and have correct group
    log('DEBUG', 'Processing user manifests')
    handle_user_manifests(users)

    # 3. Ensure smartgroup manifests exists
    log('DEBUG', 'Processing smartgroup manifests')
    handle_smartgroup_manifests(smartgroups)

    # 4. Ensure device manifest exist and have correct nested manifests
    log('DEBUG', 'Processing device manifests')
    handle_device_manifests(devices)

def sync_device(api, serial_number):
    """Syncs single device manifests"""

    devices = {}

    try:
        rawdevice = api.devices.get_details_by_alt_id(serialnumber=serial_number)
    except AirWatchAPIError:
        log('Unable to find device in AirWatch', )
        exit(1)

    id = str(rawdevice['Id']['Value'])
    devices[id] = {}
    devices[id]['id'] = id
    devices[id]['serial'] = serial_number
    devices[id]['smartgroups'] = []

    if 'UserName' in rawdevice:
        devices[id]['user'] = {'name': rawdevice['UserName']}

    # Get desired AirWatch smartgroups
    rawsmartgroups = api.smartgroups.search()
    smartgroups = extract_smartgroups(rawsmartgroups)

    # Get desired smartgroup memberships
    for smartgroup in smartgroups.values():
        rawsmartmembers = api.smartgroups.get_devices(id=smartgroup['id'])
        if isinstance(rawsmartmembers, dict):
            smartmembers = rawsmartmembers['Devices']
            # Assin smartgroups to devices
            assign_smartgroups(devices, smartgroup, smartmembers, single_device=True)

    handle_smartgroup_manifests(smartgroups)
    handle_device_manifests(devices)

# Main: run script, parse arguments anc sync those manifests - - - - - - - - - - - - - - -
def main(args):
    """Just main"""

    # Create API object
    api = AirWatchAPI(env=AIRWATCH_SERVER, apikey=APIKEY, username=USERNAME, password=PASSWORD)


    # Sync single serial number only
    if args.serial:
        print('Syncing only manifest with serial number {}'.format(args.serial))
        sync_device(api, args.serial)
        exit(0)

    # Sync all devices in regular run
    sync_all_devicec(api)
    exit(0)

if __name__ == '__main__':

    # Argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--serial", help="sync serial number only")
    args = parser.parse_args()

    main(args)