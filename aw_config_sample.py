# Script configuration - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# AirWatch access config
AIRWATCH_SERVER = "https://airwatch.url.tld"
APIKEY = ""
USERNAME = ""
PASSWORD = ""

# AirWatch script config
AIRWATCH_MAC_PLATFORM = "AppleOsX"
AIRWATCH_ALL_USERGROUPS = False
AIRWATCH_ALL_SMARTGROUPS = False
AIRWATCH_USERGROUPS = ["SomeUserGroup"]
AIRWATCH_SMARTGROUPS = ["SomeSmartGroup"]
AIRWATCH_USERS_IGNORE = ["Default Staging User", "staging"]
AIRWATCH_API_REQUEST_PAGESIZE = 500

# Munki paths config
MANIFEST_DIR = "/path/to/munki/repo/manifests"

MANIFEST_DEVICE_DIR = ""
MANIFEST_USER_DIR = "users"
MANIFEST_USERGROUP_DIR = "groups/usergroups"
MANIFEST_SMARTGROUP_DIR = "groups/smartgroups"

# Munki manifest config
DEFAULT_DEVICE_MANIFEST = {
    "catalogs": ["production"],
    "included_manifests": ["groups/all_devices"],
}

# Scrit settings
SCRIPT_VERBOSE = True
SCRIPT_LOGFILE = "/path/to/log/file.log"
