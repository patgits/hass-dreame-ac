"""Constants for the Dreame AC integration."""

DOMAIN = "dreame_ac"
DEFAULT_NAME = "Dreame AC"

# --- Dreame Cloud API ---
# Auth + command endpoints (verified against dreame.aircon.tbl2528, region eu).
AUTH_URL_TEMPLATE = "https://{region}.iot.dreame.tech:13267/dreame-auth/oauth/token"
DEVICE_LIST_URL_TEMPLATE = (
    "https://{region}.iot.dreame.tech:13267"
    "/dreame-user-iot/iotuserbind/device/listV2"
)
SEND_COMMAND_URL_TEMPLATE = (
    "https://{region}.iot.dreame.tech:13267"
    "/dreame-iot-com-{host_prefix}/device/sendCommand"
)

# App client credentials (public, identical to the iOS app build 1594).
BASIC_AUTH = "Basic ZHJlYW1lX2FwcHYxOkFQXmR2QHpAU1FZVnhOODg="
PASSWORD_SALT = "RAylYC%fmSKp7%Tq"
TENANT_ID = "000000"
USER_AGENT = "Dreame_Smarthome/2.5.7 (com.dreame.smarthome; build:1594; iOS 26.5.1)"
DREAME_META = "cv=i_1594"

DEFAULT_REGION = "eu"
DEFAULT_HOST_PREFIX = "10000"
REGIONS = ["eu", "sg", "cn", "us"]

# Token lifetime is 7200s; refresh a bit early.
TOKEN_REFRESH_MARGIN = 300
DEFAULT_SCAN_INTERVAL = 30

# --- Config entry keys ---
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_REGION = "region"
CONF_DID = "did"
CONF_HOST_PREFIX = "host_prefix"
CONF_MODEL = "model"

# --- MIoT property map (standard air-conditioner spec defaults) ---
# These are the conventional siid/piid for urn:miot-spec-v2:device:air-conditioner.
# The coordinator verifies them at runtime via property discovery and logs the
# actual values it finds; adjust here once discovery confirms the real layout of
# dreame.aircon.tbl2528.
PROP_POWER = (2, 1)          # bool
PROP_MODE = (2, 2)           # enum
PROP_TARGET_TEMP = (2, 4)    # float / int
PROP_CURRENT_TEMP = (4, 1)   # float (environment service)
PROP_FAN_LEVEL = (3, 2)      # enum
PROP_SWING = (3, 4)          # bool (horizontal/vertical swing)

# Range scanned during first-connect discovery.
DISCOVERY_SIIDS = range(1, 8)
DISCOVERY_PIIDS = range(1, 16)

# MIoT mode int -> HA HVAC mode (defaults; verified at runtime).
MODE_TO_HVAC = {0: "cool", 1: "heat", 2: "auto", 3: "dry", 4: "fan_only"}
# MIoT fan int -> HA fan mode.
FAN_TO_HA = {0: "auto", 1: "low", 2: "medium", 3: "high"}
