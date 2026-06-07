"""Constants for the Dreame AC integration (dreame.aircon.tbl2528)."""

DOMAIN = "dreame_ac"
DEFAULT_NAME = "Dreame AC"

# --- Dreame Cloud API ---
AUTH_URL_TEMPLATE = "https://{region}.iot.dreame.tech:13267/dreame-auth/oauth/token"
DEVICE_LIST_URL_TEMPLATE = (
    "https://{region}.iot.dreame.tech:13267"
    "/dreame-user-iot/iotuserbind/device/listV2"
)
SEND_COMMAND_URL_TEMPLATE = (
    "https://{region}.iot.dreame.tech:13267"
    "/dreame-iot-com-{host_prefix}/device/sendCommand"
)

BASIC_AUTH = "Basic ZHJlYW1lX2FwcHYxOkFQXmR2QHpAU1FZVnhOODg="
PASSWORD_SALT = "RAylYC%fmSKp7%Tq"
TENANT_ID = "000000"
USER_AGENT = "Dreame_Smarthome/2.5.7 (com.dreame.smarthome; build:1594; iOS 26.5.1)"
DREAME_META = "cv=i_1594"

DEFAULT_REGION = "eu"
DEFAULT_HOST_PREFIX = "10000"
REGIONS = ["eu", "sg", "cn", "us"]

TOKEN_REFRESH_MARGIN = 300
DEFAULT_SCAN_INTERVAL = 30

# --- Config entry keys ---
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_REGION = "region"
CONF_DID = "did"
CONF_HOST_PREFIX = "host_prefix"
CONF_MODEL = "model"

# ---------------------------------------------------------------------------
# REAL property map for dreame.aircon.tbl2528 (fully reverse-engineered).
#   2.1  power           bool
#   2.2  mode            1=cool  2=dry  4=fan
#   2.3  target temp     int, °C * 10
#   3.5  night mode      bool
#   4.2  swing/oscillate bool
#   10.1 current temp    int, °C * 10  (read-only)
# Fan SPEED is NOT exposed over the cloud RPC — device limitation.
#   Verified empirically: across Low/High (via app AND remote) siid 2.4 stays
#   constant at 2 and siid 8.1 stays constant at 0; no property tracks the
#   fan-speed change, so it cannot be read or set over the cloud.
# ---------------------------------------------------------------------------
PROP_POWER = (2, 1)
PROP_MODE = (2, 2)
PROP_TARGET_TEMP = (2, 3)
PROP_NIGHT = (3, 5)
PROP_SWING = (4, 2)
PROP_CURRENT_TEMP = (10, 1)

TEMP_SCALE = 10
MIN_TEMP = 16
MAX_TEMP = 31

# Device mode int <-> HA HVAC mode (this is a cooling-only unit: no heat).
MODE_TO_HVAC = {1: "cool", 2: "dry", 4: "fan_only"}
