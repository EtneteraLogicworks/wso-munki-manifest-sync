# README

Script `aw_munki_manifest_sync.py` uses VMware Workspace ONE UEM API (formerly AirWatch)
to retrive information about relationships between following objects:

- enrolled macOS **devices**
- device **enrollment users**
- **smartgroups** devices are members of
- **usergroups** enrollment users are members of

Next it creates Munki manifest structure mirroring current state of WSO object
relationships.


## Dependencies

`aw_munki_manifest_sync.py` was written to be compatible with both Python 2 and Python 3.
However Python 2 compatibility is no longer tested and might be dropped in the near
future.

Script uses [PyVMwareAirWatch](https://github.com/jprichards/PyVMwareAirWatch) library
created by VMware developer [jprichards](https://github.com/jprichards). Submodule
in this repo is the [fork](https://github.com/EtneteraLogicworks/PyVMwareAirWatch) of
`PyVMwareAirWatch` library.


## Operation

When ran without any options, script synchronizes all macOS devices, with enrollment
users, user's usergroups and device's smartgroups. Intention is to run script at regular
intervals. It is possible to run the synchronization only for a single device (See
`--serial` option bellow).

If manifest file does not exist script will create it. Script does not create directories.
Administrator must create all necessary directories before running the script.

If relationship between device, user, usergroup or smargroup has changed, list of nested
manifest in device or user manifest is updated. Manifest files are never deleted
by this script.

Only manifests containing `airwatch_` string are managed by this script (with exception
of device manifests named using only serial number). Administrator can edit all manifest
created by `aw_munki_manifest_sync.py`.

### Options

- `--serial SERIAL_NUMBER` causes script only to synchronize single device using
   provided serial number. Intention is to run this during the device enrollment
   shorty after user is assigned to the device.

### Example

WSO state:

- Device: `C02HW5123456`
- Device `C02HW5123456` Enrollment User: `bob`
- User `bob` is member of Usergroups: [ `g1`, `g2` ]
- Device `C02HW5123456` is member of Smartgroups: [ `sg1` ]

Will result in following Munki manifest structure:

- `manifests/C02HW5123456`
    - nested manifest `users/airwatch_user_bob`:
    - nested manifest `groups/smartgroups/airwatch_smartgroup_sg1`
- `manifests/groups/smartgroups/airwatch_smartgroup_sg1`
- `manifests/users/airwatch_user_bob`
    - nested manifest `groups/usergroups/airwatch_usergroup_g1`:
    - nested manifest `groups/usergroups/airwatch_usergroup_g2`
- `manifests/groups/usergroups/airwatch_usergroup_g1`
- `manifests/groups/usergroups/airwatch_usergroup_g2`


## Configuration

Script is configured via config file `aw_config.py` which must be located in the
same directory as script itself.

| Key                       | Type       |                            |
| ------------------------- | ---------- | -------------------------- |
| AIRWATCH_SERVER           | String     | AirWatch server URL        |
| APIKEY                    | String     | AirWatch API key           |
| USERNAME                  | String     | AirWatch API user name     |
| PASSWORD                  | String     | AirWatch API user password |
|                           |            |                            |
| AIRWATCH_MAC_PLATFORM     | String     | AirWatch Mac platform identifier. Should be left to default `AppleOsX`  |
| AIRWATCH_ALL_USERGROUPS   | Boolean    | If True script will attempt to sync all usergroups |
| AIRWATCH_ALL_SMARTGROUPS  | Boolean    | If True script will attempt to sync all smartgroups |
| AIRWATCH_USERGROUPS       | Array      | List of usergroups which should be synced |
| AIRWATCH_SMARTGROUPS      | Array      | List of smartgroups which should be synced |
| AIRWATCH_USERS_IGNORE     | Array      | List of user which should not be synced. Good for exlucing staging users |
|                           |            |                            |
| MANIFEST_DIR              | Path       | Absolute path to manifest directory |
| MANIFEST_DEVICE_DIR       | String     | Relative path to device manifest subdirectory |
| MANIFEST_USER_DIR         | String     | Relative path to user manifest subdirectory |
| MANIFEST_USERGROUP_DIR    | String     | Relative path to usergroup manifest subdirectory |
| MANIFEST_SMARTGROUP_DIR   | String     | Relative path to smarrgroup manifest subdirectory |
| DEFAULT_DEVICE_MANIFEST   | Dictionary | Template to use when creating new manifest file |
|                           |            |                            |
| SCRIPT_VERBOSE            | Boolean    | Enable verbose logging     |
| SCRIPT_LOGFILE            | Path       | If defined, script will log to file |
