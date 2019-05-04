import logging
import voluptuous as vol
import json
from datetime import timedelta
import time

from homeassistant.components import sensor
from custom_components.smartthinq import (
	DOMAIN, LGE_DEVICES, LGEDevice)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA  # noqa
from homeassistant.const import (
    ATTR_ENTITY_ID, CONF_NAME, CONF_TOKEN, CONF_ENTITY_ID)
from homeassistant.exceptions import PlatformNotReady

import wideq

LGE_WASHER_DEVICES = 'lge_washer_devices'
LGE_DRYER_DEVICES = 'lge_dryer_devices'
LGE_WATERPURIFIER_DEVICES = 'lge_waterpurifier_devices'

CONF_MAC = 'mac'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_MAC): cv.string,
})

# For WASHER
#-----------------------------------------------------------
ATTR_CURRENT_STATUS = 'current_status'
ATTR_RUN_STATE = 'run_state'
ATTR_PRE_STATE = 'pre_state'
ATTR_REMAIN_TIME = 'remain_time'
ATTR_INITIAL_TIME = 'initial_time'
ATTR_RESERVE_TIME = 'reserve_time'
ATTR_CURRENT_COURSE = 'current_course'
ATTR_ERROR_STATE = 'error_state'
ATTR_WASH_OPTION_STATE = 'wash_option_state'
ATTR_SPIN_OPTION_STATE = 'spin_option_state'
ATTR_WATERTEMP_OPTION_STATE = 'watertemp_option_state'
ATTR_RINSECOUNT_OPTION_STATE = 'rinsecount_option_state'
ATTR_DRYLEVEL_STATE = 'drylevel_state'
ATTR_FRESHCARE_MODE = 'freshcare_mode'
ATTR_CHILDLOCK_MODE = 'childlock_mode'
ATTR_STEAM_MODE = 'steam_mode'
ATTR_TURBOSHOT_MODE = 'turboshot_mode'
ATTR_TUBCLEAN_COUNT = 'tubclean_count'
ATTR_LOAD_LEVEL = 'load_level'
ATTR_DEVICE_TYPE = 'device_type'
ATTR_RINSE_OPTION_STATE = 'rinse_option_state'

WASHERRUNSTATES = {
    'OFF': wideq.STATE_WASHER_POWER_OFF,
    'INITIAL': wideq.STATE_WASHER_INITIAL,
    'PAUSE': wideq.STATE_WASHER_PAUSE,
    'ERROR_AUTO_OFF': wideq.STATE_WASHER_ERROR_AUTO_OFF,
    'RESERVE': wideq.STATE_WASHER_RESERVE,
    'DETECTING': wideq.STATE_WASHER_DETECTING,
    'ADD_DRAIN': wideq.STATE_WASHER_ADD_DRAIN,
    'DETERGENT_AMOUNT': wideq.STATE_WASHER_DETERGENT_AMOUT,
    'RUNNING': wideq.STATE_WASHER_RUNNING,
    'PREWASH': wideq.STATE_WASHER_PREWASH,
    'RINSING': wideq.STATE_WASHER_RINSING,
    'RINSE_HOLD': wideq.STATE_WASHER_RINSE_HOLD,
    'SPINNING': wideq.STATE_WASHER_SPINNING,
    'DRYING': wideq.STATE_WASHER_DRYING,
    'END': wideq.STATE_DRYER_END,
    'FRESHCARE': wideq.STATE_WASHER_FRESHCARE,
    'TCL_ALARM_NORMAL': wideq.STATE_WASHER_TCL_ALARM_NORMAL,
    'FROZEN_PREVENT_INITIAL': wideq.STATE_WASHER_FROZEN_PREVENT_INITIAL,
    'FROZEN_PREVENT_RUNNING': wideq.STATE_WASHER_FROZEN_PREVENT_RUNNING,
    'FROZEN_PREVENT_PAUSE': wideq.STATE_WASHER_FROZEN_PREVENT_PAUSE,
    'ERROR': wideq.STATE_WASHER_ERROR,
}

SOILLEVELSTATES = {
    'NO_SELECT': wideq.STATE_WASHER_TERM_NO_SELECT,
    'LIGHT': wideq.STATE_WASHER_SOILLEVEL_LIGHT,
    'NORMAL': wideq.STATE_WASHER_SOILLEVEL_NORMAL,
    'HEAVY': wideq.STATE_WASHER_SOILLEVEL_HEAVY,
    'PRE_WASH': wideq.STATE_WASHER_SOILLEVEL_PRE_WASH,
    'SOAKING': wideq.STATE_WASHER_SOILLEVEL_SOAKING,
    'OFF': wideq.STATE_WASHER_POWER_OFF,

}

WATERTEMPSTATES = {
    'NO_SELECT': wideq.STATE_WASHER_TERM_NO_SELECT,
    'COLD' : wideq.STATE_WASHER_WATERTEMP_COLD,
    'TWENTY' : wideq.STATE_WASHER_WATERTEMP_20,
    'THIRTY' : wideq.STATE_WASHER_WATERTEMP_30,
    'FOURTY' : wideq.STATE_WASHER_WATERTEMP_40,
    'SIXTY': wideq.STATE_WASHER_WATERTEMP_60,
    'NINTYFIVE': wideq.STATE_WASHER_WATERTEMP_95,
    'OFF': wideq.STATE_WASHER_POWER_OFF,

    #'NO_SELECT': wideq.STATE_WASHER_TERM_NO_SELECT,
    #'COLD' : wideq.STATE_WASHER_WATERTEMP_COLD,
    #'THIRTY' : wideq.STATE_WASHER_WATERTEMP_30,
    #'FOURTY' : wideq.STATE_WASHER_WATERTEMP_40,
    #'SIXTY': wideq.STATE_WASHER_WATERTEMP_60,
    #'NINTYFIVE': wideq.STATE_WASHER_WATERTEMP_95,
    #'OFF': wideq.STATE_WASHER_POWER_OFF,
}

SPINSPEEDSTATES = {
    'NOSPIN': wideq.STATE_WASHER_SPINSPEED_NOSPIN,
    'SPIN_400' : wideq.STATE_WASHER_SPINSPEED_400,
    'SPIN_800' : wideq.STATE_WASHER_SPINSPEED_800,
    'SPIN_1000' : wideq.STATE_WASHER_SPINSPEED_1000,
    'SPIN_1200': wideq.STATE_WASHER_SPINSPEED_1200,
    'SPIN_1400': wideq.STATE_WASHER_SPINSPEED_1400,
    'OFF': wideq.STATE_WASHER_POWER_OFF,
    #'NO_SELECT': wideq.STATE_WASHER_TERM_NO_SELECT,
    #'EXTRA_LOW' : wideq.STATE_WASHER_SPINSPEED_EXTRA_LOW,
    #'LOW' : wideq.STATE_WASHER_SPINSPEED_LOW,
    #'MEDIUM' : wideq.STATE_WASHER_SPINSPEED_MEDIUM,
    #'HIGH': wideq.STATE_WASHER_SPINSPEED_HIGH,
    #'EXTRA_HIGH': wideq.STATE_WASHER_SPINSPEED_EXTRA_HIGH,
    #'OFF': wideq.STATE_WASHER_POWER_OFF,
}

RINSECOUNTSTATES = {
    'NO_SELECT': wideq.STATE_WASHER_TERM_NO_SELECT,
    'ONE' : wideq.STATE_WASHER_RINSECOUNT_1,
    'TWO' : wideq.STATE_WASHER_RINSECOUNT_2,
    'THREE' : wideq.STATE_WASHER_RINSECOUNT_3,
    'FOUR': wideq.STATE_WASHER_RINSECOUNT_4,
    'FIVE': wideq.STATE_WASHER_RINSECOUNT_5,
    'OFF': wideq.STATE_WASHER_POWER_OFF,
}

RINSEOPTIONSTATES = {
    'NORMAL': wideq.STATE_WASHER_RINSE_NORMAL,
    'EXTRA_RINSE': wideq.STATE_WASHER_EXTRA_RINSE
}

DRYLEVELSTATES = {
    'NO_SELECT': wideq.STATE_WASHER_TERM_NO_SELECT,
    'WIND' : wideq.STATE_WASHER_DRYLEVEL_WIND,
    'TURBO' : wideq.STATE_WASHER_DRYLEVEL_TURBO,
    'TIME_30' : wideq.STATE_WASHER_DRYLEVEL_TIME_30,
    'TIME_60': wideq.STATE_WASHER_DRYLEVEL_TIME_60,
    'TIME_90': wideq.STATE_WASHER_DRYLEVEL_TIME_90,
    'TIME_120': wideq.STATE_WASHER_DRYLEVEL_TIME_120,
    'TIME_150': wideq.STATE_WASHER_DRYLEVEL_TIME_150,
    'OFF': wideq.STATE_WASHER_POWER_OFF,
}

WASHERERRORS = {
    'ERROR_dE2' : wideq.STATE_WASHER_ERROR_dE2,
    'ERROR_IE' : wideq.STATE_WASHER_ERROR_IE,
    'ERROR_OE' : wideq.STATE_WASHER_ERROR_OE,
    'ERROR_UE' : wideq.STATE_WASHER_ERROR_UE,
    'ERROR_FE' : wideq.STATE_WASHER_ERROR_FE,
    'ERROR_PE' : wideq.STATE_WASHER_ERROR_PE,
    'ERROR_tE' : wideq.STATE_WASHER_ERROR_tE,
    'ERROR_LE' : wideq.STATE_WASHER_ERROR_LE,
    'ERROR_CE' : wideq.STATE_WASHER_ERROR_CE,
    'ERROR_PF' : wideq.STATE_WASHER_ERROR_PF,
    'ERROR_FF' : wideq.STATE_WASHER_ERROR_FF,
    'ERROR_dCE' : wideq.STATE_WASHER_ERROR_dCE,
    'ERROR_EE' : wideq.STATE_WASHER_ERROR_EE,
    'ERROR_PS' : wideq.STATE_WASHER_ERROR_PS,
    'ERROR_dE1' : wideq.STATE_WASHER_ERROR_dE1,
    'ERROR_LOE' : wideq.STATE_WASHER_ERROR_LOE,        
    'NO_ERROR' : wideq.STATE_NO_ERROR,
    'OFF': wideq.STATE_DRYER_POWER_OFF,
}

OPTIONITEMMODES = {
    'ON': wideq.STATE_OPTIONITEM_ON,
    'OFF': wideq.STATE_OPTIONITEM_OFF,
}

# For DRYER
#-----------------------------------------------------------
ATTR_DRYLEVEL_STATE = 'drylevel_state'
ATTR_ECOHYBRID_STATAE = 'ecohybrid_state'
ATTR_ECOHYBRID_LIST = 'ecohybrid_list'
ATTR_PROCESS_STATE = 'process_state'
ATTR_CURRENT_SMARTCOURSE = 'current_smartcourse'
ATTR_ANTICREASE_MODE = 'anticrease_mode'
ATTR_SELFCLEANING_MODE = 'selfcleaning_mode'
ATTR_DAMPDRYBEEP_MODE = 'dampdrybeep_mode'
ATTR_HANDIRON_MODE = 'handiron_mode'
ATTR_RESERVE_INITIAL_TIME = 'reserve_initial_time'
ATTR_RESERVE_REMAIN_TIME = 'reserve_remain_time'
ATTR_DEVICE_TYPE = 'device_type'

DRYERRUNSTATES = {
    'OFF': wideq.STATE_DRYER_POWER_OFF,
    'INITIAL': wideq.STATE_DRYER_INITIAL,
    'RUNNING': wideq.STATE_DRYER_RUNNING,
    'PAUSE': wideq.STATE_DRYER_PAUSE,
    'END': wideq.STATE_DRYER_END,
    'ERROR': wideq.STATE_DRYER_ERROR,
}

PROCESSSTATES = {
    'DETECTING': wideq.STATE_DRYER_PROCESS_DETECTING,
    'STEAM': wideq.STATE_DRYER_PROCESS_STEAM,
    'DRY': wideq.STATE_DRYER_PROCESS_DRY,
    'COOLING': wideq.STATE_DRYER_PROCESS_COOLING,
    'ANTI_CREASE': wideq.STATE_DRYER_PROCESS_ANTI_CREASE,
    'END': wideq.STATE_DRYER_PROCESS_END,
    'OFF': wideq.STATE_DRYER_POWER_OFF,
}

DRYLEVELMODES = {
    'IRON' : wideq.STATE_DRY_LEVEL_IRON,
    'CUPBOARD' : wideq.STATE_DRY_LEVEL_CUPBOARD,
    'EXTRA' : wideq.STATE_DRY_LEVEL_EXTRA,
    'OFF': wideq.STATE_DRYER_POWER_OFF,    
}

ECOHYBRIDMODES = {
    'ECO' : wideq.STATE_ECOHYBRID_ECO,
    'NORMAL' : wideq.STATE_ECOHYBRID_NORMAL,
    'TURBO' : wideq.STATE_ECOHYBRID_TURBO,
    'OFF': wideq.STATE_DRYER_POWER_OFF,    
}

COURSES = {
    'Cotton Soft_타월' : wideq.STATE_COURSE_COTTON_SOFT,
    'Bulky Item_이불' : wideq.STATE_COURSE_BULKY_ITEM,
    'Easy Care_셔츠' : wideq.STATE_COURSE_EASY_CARE,
    'Cotton_표준' : wideq.STATE_COURSE_COTTON,
    'Sports Wear_기능성의류' : wideq.STATE_COURSE_SPORTS_WEAR,
    'Quick Dry_급속' : wideq.STATE_COURSE_QUICK_DRY,
    'Wool_울/섬세' : wideq.STATE_COURSE_WOOL,
    'Rack Dry_선반 건조' : wideq.STATE_COURSE_RACK_DRY,
    'Cool Air_송풍' : wideq.STATE_COURSE_COOL_AIR,        
    'Warm Air_온풍' : wideq.STATE_COURSE_WARM_AIR,
    '침구털기' : wideq.STATE_COURSE_BEDDING_BRUSH,
    'Sterilization_살균' : wideq.STATE_COURSE_STERILIZATION,
    'Power_강력' : wideq.STATE_COURSE_POWER,
    'Refresh': wideq.STATE_COURSE_REFRESH,
    'OFF': wideq.STATE_DRYER_POWER_OFF,
}

SMARTCOURSES = {
    'Gym Clothes_운동복' : wideq.STATE_SMARTCOURSE_GYM_CLOTHES,
    'Rainy Season_장마철' : wideq.STATE_SMARTCOURSE_RAINY_SEASON,
    'Deodorization_리프레쉬' : wideq.STATE_SMARTCOURSE_DEODORIZATION,
    'Small Load_소량 건조' : wideq.STATE_SMARTCOURSE_SMALL_LOAD,
    'Lingerie_란제리' : wideq.STATE_SMARTCOURSE_LINGERIE,
    'Easy Iron_촉촉 건조' : wideq.STATE_SMARTCOURSE_EASY_IRON,
    'SUPER_DRY' : wideq.STATE_SMARTCOURSE_SUPER_DRY,
    'Economic Dry_절약 건조' : wideq.STATE_SMARTCOURSE_ECONOMIC_DRY,
    'Big Size Item_큰 빨래 건조' : wideq.STATE_SMARTCOURSE_BIG_SIZE_ITEM,
    'Minimize Wrinkles_구김 완화 건조' : wideq.STATE_SMARTCOURSE_MINIMIZE_WRINKLES,
    'Full Size Load_다량 건조' : wideq.STATE_SMARTCOURSE_FULL_SIZE_LOAD,
    'Jean_청바지' : wideq.STATE_SMARTCOURSE_JEAN,
    'OFF': wideq.STATE_DRYER_POWER_OFF,

}

DRYERERRORS = {
    'ERROR_DOOR' : wideq.STATE_ERROR_DOOR,
    'ERROR_DRAINMOTOR' : wideq.STATE_ERROR_DRAINMOTOR,
    'ERROR_LE1' : wideq.STATE_ERROR_LE1,
    'ERROR_TE1' : wideq.STATE_ERROR_TE1,
    'ERROR_TE2' : wideq.STATE_ERROR_TE2,
    'ERROR_F1' : wideq.STATE_ERROR_F1,
    'ERROR_LE2' : wideq.STATE_ERROR_LE2,
    'ERROR_AE' : wideq.STATE_ERROR_AE,
    'ERROR_dE4' : wideq.STATE_ERROR_dE4,
    'ERROR_NOFILTER' : wideq.STATE_ERROR_NOFILTER,
    'ERROR_EMPTYWATER' : wideq.STATE_ERROR_EMPTYWATER,
    'ERROR_CE1' : wideq.STATE_ERROR_CE1,
    'NO_ERROR' : wideq.STATE_NO_ERROR,
    'OFF': wideq.STATE_DRYER_POWER_OFF,
}

OPTIONITEMMODES = {
    'ON': wideq.STATE_OPTIONITEM_ON,
    'OFF': wideq.STATE_OPTIONITEM_OFF,
}

# For WATER PURIFIER
#-----------------------------------------------------------
ATTR_COLD_WATER_USAGE_DAY = 'cold_water_usage_day'
ATTR_NORMAL_WATER_USAGE_DAY = 'normal_water_usage_day'
ATTR_HOT_WATER_USAGE_DAY = 'hot_water_usage_day'
ATTR_TOTAL_WATER_USAGE_DAY = 'total_water_usage_day'

ATTR_COLD_WATER_USAGE_WEEK = 'cold_water_usage_week'
ATTR_NORMAL_WATER_USAGE_WEEK = 'normal_water_usage_week'
ATTR_HOT_WATER_USAGE_WEEK = 'hot_water_usage_week'
ATTR_TOTAL_WATER_USAGE_WEEK = 'total_water_usage_week'

ATTR_COLD_WATER_USAGE_MONTH = 'cold_water_usage_month'
ATTR_NORMAL_WATER_USAGE_MONTH = 'normal_water_usage_month'
ATTR_HOT_WATER_USAGE_MONTH = 'hot_water_usage_month'
ATTR_TOTAL_WATER_USAGE_MONTH = 'total_water_usage_month'

ATTR_COLD_WATER_USAGE_YEAR = 'cold_water_usage_year'
ATTR_NORMAL_WATER_USAGE_YEAR = 'normal_water_usage_year'
ATTR_HOT_WATER_USAGE_YEAR = 'hot_water_usage_year'
ATTR_TOTAL_WATER_USAGE_YEAR = 'total_water_usage_year'

ATTR_COCKCLEAN_STATE = 'cockcelan_state'
ATTR_DEVICE_TYPE = 'device_type'

COCKCLEANMODES = {
    'WAITING': wideq.STATE_WATERPURIFIER_COCKCLEAN_WAIT,
    'COCKCLEANING': wideq.STATE_WATERPURIFIER_COCKCLEAN_ON,
}

MAX_RETRIES = 5

LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    import wideq
    refresh_token = hass.data[CONF_TOKEN]
    client = wideq.Client.from_token(refresh_token)
    name = config[CONF_NAME]
    conf_mac = config[CONF_MAC]

    """Set up the LGE entity."""
    for device_id in hass.data[LGE_DEVICES]:
        device = client.get_device(device_id)
        model = client.model_info(device)
        model_type = model.model_type
        mac = device.macaddress
        if device.type == wideq.DeviceType.WASHER:
            LGE_WASHER_DEVICES = []
            if mac == conf_mac.lower():
                LOGGER.debug("Creating new LGE Washer")
                try:
                    washer_entity = LGEWASHERDEVICE(client, device, name, model_type)
                except wideq.NotConnectError:
                    LOGGER.info('Connection Lost. Retrying.')
                    raise PlatformNotReady
                LGE_WASHER_DEVICES.append(washer_entity)
                add_entities(LGE_WASHER_DEVICES)
                LOGGER.debug("LGE Washer is added")
        if device.type == wideq.DeviceType.DRYER:
            LGE_DRYER_DEVICES = []
            if mac == conf_mac.lower():
                LOGGER.debug("Creating new LGE Dryer")
                try:
                    dryer_entity = LGEDRYERDEVICE(client, device, name, model_type)
                except wideq.NotConnectError:
                    raise PlatformNotReady
                LGE_DRYER_DEVICES.append(dryer_entity)
                add_entities(LGE_DRYER_DEVICES)
                LOGGER.debug("LGE Dryer is added")
        if device.type == wideq.DeviceType.WATER_PURIFIER:
            LGE_WATERPURIFIER_DEVICES = []
            if mac == conf_mac.lower():
                waterpurifier_entity = LGEWATERPURIFIERDEVICE(client, device, name, model_type)
                LGE_WATERPURIFIER_DEVICES.append(waterpurifier_entity)
                add_entities(LGE_WATERPURIFIER_DEVICES)
                LOGGER.debug("LGE WATER PURIFIER is added")

# WASHER Main 
class LGEWASHERDEVICE(LGEDevice):
    def __init__(self, client, device, name, model_type):
        
        """initialize a LGE Washer Device."""
        LGEDevice.__init__(self, client, device)

        import wideq
        self._washer = wideq.WasherDevice(client, device)

        self._washer.monitor_start()
        self._washer.monitor_start()
        self._washer.delete_permission()
        self._washer.delete_permission()

        # The response from the monitoring query.
        self._state = None
        self._name = name
        self._type = model_type

        self.update()

    @property
    def name(self):
    	return self._name

    @property
    def device_type(self):
        return self._type

    @property
    def supported_features(self):
        """ none """

    @property
    def state_attributes(self):
        """Return the optional state attributes."""
        data={}
        data[ATTR_DEVICE_TYPE] = self.device_type
        data[ATTR_RUN_STATE] = self.current_run_state
        data[ATTR_PRE_STATE] = self.pre_state
        data[ATTR_REMAIN_TIME] = self.remain_time
        data[ATTR_INITIAL_TIME] = self.initial_time
        data[ATTR_RESERVE_TIME] = self.reserve_time
        data[ATTR_CURRENT_COURSE] = self.current_course
        data[ATTR_ERROR_STATE] = self.error_state
        data[ATTR_WASH_OPTION_STATE] = self.wash_option_state
        data[ATTR_SPIN_OPTION_STATE] = self.spin_option_state
        data[ATTR_WATERTEMP_OPTION_STATE] = self.watertemp_option_state
        data[ATTR_RINSECOUNT_OPTION_STATE] = self.rinsecount_option_state
        data[ATTR_DRYLEVEL_STATE] = self.drylevel_state
        data[ATTR_FRESHCARE_MODE] = self.freshcare_mode
        data[ATTR_CHILDLOCK_MODE] = self.childlock_mode
        data[ATTR_STEAM_MODE] = self.steam_mode
        data[ATTR_TURBOSHOT_MODE] = self.turboshot_mode
        data[ATTR_TUBCLEAN_COUNT] = self.tubclean_count
        data[ATTR_LOAD_LEVEL] = self.load_level
        data[ATTR_RINSE_OPTION_STATE] = self.rinse_option_state
        return data

    @property
    def state(self):
        if self._state:
            run = self._state.run_state
            return WASHERRUNSTATES[run.name]

    @property
    def current_run_state(self):
        if self._state:
            run = self._state.run_state
            return WASHERRUNSTATES[run.name]

    @property
    def pre_state(self):
        if self._state:
            pre = self._state.pre_state
            return WASHERRUNSTATES[pre.name]

    @property
    def remain_time(self):    
        if self._state:
            remain_hour = self._state.remaintime_hour
            remain_min = self._state.remaintime_min
            remaintime = [remain_hour, remain_min]
            if int(remain_min) < 10:
                return ":0".join(remaintime)
            else:
                return ":".join(remaintime)
            
    @property
    def initial_time(self):
        if self._state:
            initial_hour = self._state.initialtime_hour
            initial_min = self._state.initialtime_min
            initialtime = [initial_hour, initial_min]
            if int(initial_min) < 10:
                return ":0".join(initialtime)
            else:
                return ":".join(initialtime)

    @property
    def reserve_time(self):
        if self._state:
            reserve_hour = self._state.reservetime_hour
            reserve_min = self._state.reservetime_min
            reservetime = [reserve_hour, reserve_min]
            if int(reserve_min) < 10:
                return ":0".join(reservetime)
            else:
                return ":".join(reservetime)

    @property
    def current_course(self):
        if self._state:
            course = self._state.current_course
            smartcourse = self._state.current_smartcourse
            if course == '다운로드코스':
                return smartcourse
            elif course == 'OFF':
                return 'Off'
            else:
                return course

    @property
    def error_state(self):
        if self._state:
            error = self._state.error_state
            return WASHERERRORS[error]


    @property
    def wash_option_state(self):
        if self._state:
            wash_option = self._state.wash_option_state
            if wash_option == 'OFF':
                return SOILLEVELSTATES['OFF']
            else:
                return SOILLEVELSTATES[wash_option.name]

    @property
    def rinse_option_state(self):
        if self._state:
            rinse_option = self._state.rinse_option_state
            return RINSEOPTIONSTATES[rinse_option.name]

    @property
    def spin_option_state(self):
        if self._state:
            spin_option = self._state.spin_option_state
            if spin_option == 'OFF':
                return SPINSPEEDSTATES['OFF']
            else:
                return SPINSPEEDSTATES[spin_option.name]

    @property
    def watertemp_option_state(self):
        if self._state:
            watertemp_option = self._state.water_temp_option_state
            if watertemp_option == 'OFF':
                return WATERTEMPSTATES['OFF']
            else:
                return WATERTEMPSTATES[watertemp_option.name]

    @property
    def rinsecount_option_state(self):
        if self._state:
            rinsecount_option = self._state.rinsecount_option_state
            if rinsecount_option == 'OFF':
                return RINSECOUNTSTATES['OFF']
            else:
                return RINSECOUNTSTATES[rinsecount_option.name]

    @property
    def drylevel_state(self):
        if self._state:
            drylevel = self._state.drylevel_option_state
            if drylevel == 'OFF':
                return DRYLEVELSTATES['OFF']
            else:
                return DRYLEVELSTATES[drylevel.name]

    @property
    def freshcare_mode(self):
        if self._state:
            mode = self._state.freshcare_state
            return OPTIONITEMMODES[mode]

    @property
    def childlock_mode(self):
        if self._state:
            mode = self._state.childlock_state
            return OPTIONITEMMODES[mode]

    @property
    def steam_mode(self):
        if self._state:
            mode = self._state.steam_state
            return OPTIONITEMMODES[mode]

    @property
    def turboshot_mode(self):
        if self._state:
            mode = self._state.turboshot_state
            return OPTIONITEMMODES[mode]

    @property
    def tubclean_count(self):
        if self._state:
            return self._state.tubclean_count
    
    @property
    def load_level(self):
        if self._state:
            load_level = self._state.load_level
            if load_level == 1:
                return 'Small'
            elif load_level == 2:
                return 'Medium'
            elif load_level == 3:
                return 'Large'
            elif load_level == 4:
                return 'Extra large'
            else:
                return 'Unknown'

    def update(self):

        import wideq

        LOGGER.info('Updating %s.', self.name)
        for iteration in range(MAX_RETRIES):
            LOGGER.info('Polling...')

            try:
                state = self._washer.poll()
            except wideq.NotLoggedInError:
                LOGGER.info('Session expired. Refreshing.')
                self._client.refresh()
                self._washer.monitor_start()
                self._washer.monitor_start()
                self._washer.delete_permission()
                self._washer.delete_permission()

                continue

            except wideq.NotConnectError:
                LOGGER.info('Connection Lost. Retrying.')
                self._client.refresh()
                time.sleep(60)
                continue

            if state:
                LOGGER.info('Status updated.')
                self._state = state
                self._client.refresh()
                self._washer.monitor_start()
                self._washer.monitor_start()
                self._washer.delete_permission()
                self._washer.delete_permission()
                return

            LOGGER.info('No status available yet.')
            time.sleep(2 ** iteration)

        # We tried several times but got no result. This might happen
        # when the monitoring request gets into a bad state, so we
        # restart the task.
        LOGGER.warn('Status update failed.')

        self._washer.monitor_start()
        self._washer.monitor_start()
        self._washer.delete_permission()
        self._washer.delete_permission()

# DRYER Main
class LGEDRYERDEVICE(LGEDevice):
    def __init__(self, client, device, name, model_type):
        
        """initialize a LGE Dryer Device."""
        LGEDevice.__init__(self, client, device)

        import wideq
        self._dryer = wideq.DryerDevice(client, device)

        self._dryer.monitor_start()
        self._dryer.monitor_start()
        self._dryer.delete_permission()
        self._dryer.delete_permission()

        # The response from the monitoring query.
        self._state = None
        self._name = name
        self._type = model_type
        
        self.update()

    @property
    def name(self):
    	return self._name

    @property
    def device_type(self):
        return self._type

    @property
    def supported_features(self):
        """ none """

    @property
    def state_attributes(self):
        """Return the optional state attributes."""
        data={}
        data[ATTR_DEVICE_TYPE] = self.device_type
        data[ATTR_RUN_STATE] = self.current_run_state
        data[ATTR_REMAIN_TIME] = self.remain_time
        data[ATTR_INITIAL_TIME] = self.initial_time
        data[ATTR_RESERVE_REMAIN_TIME] = self.reserve_remain_time
        data[ATTR_RESERVE_INITIAL_TIME] = self.reserve_initial_time
        data[ATTR_CURRENT_COURSE] = self.current_course
        data[ATTR_CURRENT_SMARTCOURSE] = self.current_smartcourse
        data[ATTR_ERROR_STATE] = self.error_state
        data[ATTR_DRYLEVEL_STATE] = self.drylevel_state
        data[ATTR_ECOHYBRID_STATAE] = self.ecohybrid_state
        data[ATTR_PROCESS_STATE] = self.current_process_state
        data[ATTR_ANTICREASE_MODE] = self.anticrease_mode
        data[ATTR_CHILDLOCK_MODE] = self.childlock_mode
        data[ATTR_SELFCLEANING_MODE] = self.selfcleaning_mode
        data[ATTR_DAMPDRYBEEP_MODE] = self.dampdrybeep_mode
        data[ATTR_HANDIRON_MODE] = self.handiron_mode
        return data
    
    @property
    def is_on(self):
        if self._state:
            return self._state.is_on

    @property
    def state(self):
        if self._state:
            run = self._state.run_state
            return DRYERRUNSTATES[run.name]

    @property
    def current_run_state(self):
        if self._state:
            run = self._state.run_state
            return DRYERRUNSTATES[run.name]

    @property
    def remain_time(self):    
        if self._state:
            remain_hour = self._state.remaintime_hour
            remain_min = self._state.remaintime_min
            remaintime = [remain_hour, remain_min]
            if int(remain_min) < 10:
                return ":0".join(remaintime)
            else:
                return ":".join(remaintime)
            
    @property
    def initial_time(self):
        if self._state:
            initial_hour = self._state.initialtime_hour
            initial_min = self._state.initialtime_min
            initialtime = [initial_hour, initial_min]
            if int(initial_min) < 10:
                return ":0".join(initialtime)
            else:
                return ":".join(initialtime)

    @property
    def reserve_remain_time(self):
        if self._state:
            reserve_hour = self._state.reservetime_hour
            reserve_min = self._state.reservetime_min
            reservetime = [reserve_hour, reserve_min]
            if int(reserve_min) < 10:
                return ":0".join(reservetime)
            else:
                return ":".join(reservetime)

    @property
    def reserve_initial_time(self):
        if self._state:
            reserveinitial_hour = self._state.reserveinitialtime_hour
            reserveinitial_min = self._state.reserveinitialtime_min
            reserveinitialtime = [reserveinitial_hour, reserveinitial_min]
            if int(reserveinitial_min) < 10:
                return ":0".join(reserveinitialtime)
            else:
                return ":".join(reserveinitialtime)

    @property
    def current_course(self):
        if self._state:
            course = self._state.current_course
            return COURSES[course]

    @property
    def current_smartcourse(self):
        if self._state:
            smartcourse = self._state.current_smartcourse
            return SMARTCOURSES[smartcourse]

    @property
    def error_state(self):
        if self._state:
            error = self._state.error_state
            return DRYERERRORS[error]

    @property
    def drylevel_state(self):
        if self._state:
            drylevel = self._state.drylevel_state
            if drylevel == 'OFF':
                return DRYLEVELMODES['OFF']
            else:
                return DRYLEVELMODES[drylevel.name]

    @property
    def ecohybrid_state(self):
        if self._state:
            ecohybrid = self._state.ecohybrid_state
            if ecohybrid == 'OFF':
                return ECOHYBRIDMODES['OFF']
            else:
                return ECOHYBRIDMODES[ecohybrid.name]
        
    @property
    def current_process_state(self):
        if self._state:
            process = self._state.process_state
            if self.is_on == False:
                return PROCESSSTATES['OFF']
            else:
                return PROCESSSTATES[process.name]

    @property
    def anticrease_mode(self):
        if self._state:
            mode = self._state.anticrease_state
            return OPTIONITEMMODES[mode]

    @property
    def childlock_mode(self):
        if self._state:
            mode = self._state.childlock_state
            return OPTIONITEMMODES[mode]

    @property
    def selfcleaning_mode(self):
        if self._state:
            mode = self._state.selfcleaning_state
            return OPTIONITEMMODES[mode]

    @property
    def dampdrybeep_mode(self):
        if self._state:
            mode = self._state.dampdrybeep_state
            return OPTIONITEMMODES[mode]

    @property
    def handiron_mode(self):
        if self._state:
            mode = self._state.handiron_state
            return OPTIONITEMMODES[mode]

    def update(self):

        import wideq

        LOGGER.info('Updating %s.', self.name)
        for iteration in range(MAX_RETRIES):
            LOGGER.info('Polling...')

            try:
                state = self._dryer.poll()
            except wideq.NotLoggedInError:
                LOGGER.info('Session expired. Refreshing.')
                self._client.refresh()
                self._dryer.monitor_start()
                self._dryer.monitor_start()
                self._dryer.delete_permission()
                self._dryer.delete_permission()

                continue

            if state:
                LOGGER.info('Status updated.')
                self._state = state
                self._client.refresh()
                self._dryer.monitor_start()
                self._dryer.monitor_start()
                self._dryer.delete_permission()
                self._dryer.delete_permission()
                return

            LOGGER.info('No status available yet.')
            time.sleep(2 ** iteration)

        # We tried several times but got no result. This might happen
        # when the monitoring request gets into a bad state, so we
        # restart the task.
        LOGGER.warn('Status update failed.')

        self._dryer.monitor_start()
        self._dryer.monitor_start()
        self._dryer.delete_permission()
        self._dryer.delete_permission()

# WATER PURIFIER Main
class LGEWATERPURIFIERDEVICE(LGEDevice):
    def __init__(self, client, device, name, model_type):
        
        """initialize a LGE WATER PURIFIER Device."""
        LGEDevice.__init__(self, client, device)

        import wideq
        self._wp = wideq.WPDevice(client, device)

        self._wp.monitor_start()
        self._wp.monitor_start()
        self._wp.delete_permission()
        self._wp.delete_permission()

        # The response from the monitoring query.
        self._state = None
        self._name = name
        self._type = model_type

        self.update()

    @property
    def name(self):
    	return self._name

    @property
    def device_type(self):
        return self._type

    @property
    def supported_features(self):
        """ none """

    @property
    def state_attributes(self):
        """Return the optional state attributes."""
        data={}
        data[ATTR_DEVICE_TYPE] = self.device_type
        data[ATTR_COLD_WATER_USAGE_DAY] = self.cold_water_usage_day
        data[ATTR_NORMAL_WATER_USAGE_DAY] = self.normal_water_usage_day
        data[ATTR_HOT_WATER_USAGE_DAY] = self.hot_water_usage_day
        data[ATTR_TOTAL_WATER_USAGE_DAY] = self.total_water_usage_day
        data[ATTR_COLD_WATER_USAGE_WEEK] = self.cold_water_usage_week
        data[ATTR_NORMAL_WATER_USAGE_WEEK] = self.normal_water_usage_week
        data[ATTR_HOT_WATER_USAGE_WEEK] = self.hot_water_usage_week
        data[ATTR_TOTAL_WATER_USAGE_WEEK] = self.total_water_usage_week
        data[ATTR_COLD_WATER_USAGE_MONTH] = self.cold_water_usage_month
        data[ATTR_NORMAL_WATER_USAGE_MONTH] = self.normal_water_usage_month
        data[ATTR_HOT_WATER_USAGE_MONTH] = self.hot_water_usage_month
        data[ATTR_TOTAL_WATER_USAGE_MONTH] = self.total_water_usage_month
        data[ATTR_COLD_WATER_USAGE_YEAR] = self.cold_water_usage_year
        data[ATTR_NORMAL_WATER_USAGE_YEAR] = self.normal_water_usage_year
        data[ATTR_HOT_WATER_USAGE_YEAR] = self.hot_water_usage_year
        data[ATTR_TOTAL_WATER_USAGE_YEAR] = self.total_water_usage_year
        data[ATTR_COCKCLEAN_STATE] = self.cockclean_status
        return data
    
    @property
    def state(self):
        if self._state:
            mode = self._state.cockclean_state
            return COCKCLEANMODES[mode.name]
        else:
            return '꺼짐'

    @property
    def cold_water_usage_day(self):
        data = self._wp.day_water_usage('C')
        usage = format((float(data) * 0.001), ".3f")
        return usage

    @property
    def normal_water_usage_day(self):
        data = self._wp.day_water_usage('N')
        usage = format((float(data) * 0.001), ".3f")
        return usage
      
    @property
    def hot_water_usage_day(self):
        data = self._wp.day_water_usage('H')
        usage = format((float(data) * 0.001), ".3f")
        return usage

    @property
    def total_water_usage_day(self):
        cold = self.cold_water_usage_day
        normal = self.normal_water_usage_day
        hot = self.hot_water_usage_day
        total = format((float(cold) + float(normal) + float(hot)), ".3f")
        return total

    @property
    def cold_water_usage_week(self):
        data = self._wp.week_water_usage('C')
        usage = format((float(data) * 0.001), ".3f")
        return usage
    
    @property
    def normal_water_usage_week(self):
        data = self._wp.week_water_usage('N')
        usage = format((float(data) * 0.001), ".3f")
        return usage
    @property
    def hot_water_usage_week(self):
        data = self._wp.week_water_usage('H')
        usage = format((float(data) * 0.001), ".3f")
        return usage

    @property
    def total_water_usage_week(self):
        cold = self.cold_water_usage_week
        normal = self.normal_water_usage_week
        hot = self.hot_water_usage_week
        total = format((float(cold) + float(normal) + float(hot)), ".3f")
        return total

    @property
    def cold_water_usage_month(self):
        data = self._wp.month_water_usage('C')
        usage = format((float(data) * 0.001), ".3f")
        return usage

    @property
    def normal_water_usage_month(self):
        data = self._wp.month_water_usage('N')
        usage = format((float(data) * 0.001), ".3f")
        return usage

    @property
    def hot_water_usage_month(self):
        data = self._wp.month_water_usage('H')
        usage = format((float(data) * 0.001), ".3f")
        return usage

    @property
    def total_water_usage_month(self):
        cold = self.cold_water_usage_month
        normal = self.normal_water_usage_month
        hot = self.hot_water_usage_month
        total = format((float(cold) + float(normal) + float(hot)), ".3f")
        return total

    @property
    def cold_water_usage_year(self):
        data = self._wp.year_water_usage('C')
        usage = format((float(data) * 0.001), ".3f")
        return usage

    @property
    def normal_water_usage_year(self):
        data = self._wp.year_water_usage('N')
        usage = format((float(data) * 0.001), ".3f")
        return usage

    @property
    def hot_water_usage_year(self):
        data = self._wp.year_water_usage('H')
        usage = format((float(data) * 0.001), ".3f")
        return usage

    @property
    def total_water_usage_year(self):
        cold = self.cold_water_usage_year
        normal = self.normal_water_usage_year
        hot = self.hot_water_usage_year
        total = format((float(cold) + float(normal) + float(hot)), ".3f")
        return total

    @property
    def cockclean_status(self):
        if self._state:
            mode = self._state.cockclean_state
            return COCKCLEANMODES[mode.name]

    def update(self):

        import wideq

        LOGGER.info('Updating %s.', self.name)
        for iteration in range(MAX_RETRIES):
            LOGGER.info('Polling...')

            try:
                state = self._wp.poll()
            except wideq.NotLoggedInError:
                LOGGER.info('Session expired. Refreshing.')
                self._client.refresh()
                self._wp.monitor_start()
                self._wp.monitor_start()
                self._wp.delete_permission()
                self._wp.delete_permission()

                continue

            if state:
                LOGGER.info('Status updated.')
                self._state = state
                self._client.refresh()
                self._wp.monitor_start()
                self._wp.monitor_start()
                self._wp.delete_permission()
                self._wp.delete_permission()
                return

            LOGGER.info('No status available yet.')
            time.sleep(2 ** iteration)

        # We tried several times but got no result. This might happen
        # when the monitoring request gets into a bad state, so we
        # restart the task.
        LOGGER.warn('Status update failed.')

        self._wp.monitor_start()
        self._wp.monitor_start()
        self._wp.delete_permission()
        self._wp.delete_permission()

