# README

Script `aw_munki_manifest_sync.py` uses AirWatch API to retrive information about
relation between following objects: macOS devices, enrollment users, usergroups and device
smart groups. Next it creates Munki Manifest structure mirroring current state of AirWatch
object relations. Related user, usergroup and smartgroup manifests are added/removed
in device manifest `included_manifest` array.


## Operation

When run without any options script synchronizes relation of all macOS devices,
with enrollment users, user's usergroups and device's smartgroups.

Intention is to run script on regular intervals.

If manifest file does not exist script will create it. If relation between device and
user, usergroup or smargroup has changed list of nested manifest in device manifest is
updated. Manifest files are never deleted by this script

### Options

- `--serial SERIAL_NUMBER` causes script only to synchronizce provided serial number.
   with assigned enrollment user. Intention is to run this during device enrollment
   and link device manifest to correct group manifest with actual software items.

### Example

AirWatch state:

- Device: `C02HW5123456`
- Enrollment user for device `C02HW5P5DRVG`: `bob`
- Usergroups `bob` is member of: [ `g1`, `g2` ]
- Smartgroups `C02HW5123456` is memeber of: [ `sg1` ]

Will result in following Munki manifest structure:

- `manifests/C02HW5123456`
    - nested manifest `airwatch_user_bob`: `manifests/users/airwatch_user_bob`
    - nested manifest `airwatch_usergroup_g1`: `manifests/groups/usergroups/airwatch_usergroup_g1`
    - nested manifest `airwatch_usergroup_g2`: `manifests/groups/usergroups/airwatch_usergroup_g2`
    - nested manifest `airwatch_smartgroup_sg1`: `manifests/groups/smartgroups/airwatch_smartgroup_sg1`

## Configuration

Script is configured via config file `aw_config.py` which must be located in same directory
as script itself.

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



