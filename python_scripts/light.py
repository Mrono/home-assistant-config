nightBrightness = 25
maxBrightness   = 255
dim             = 50
bright          = maxBrightness


sun             = hass.states.get('sun.sun')
now             = datetime.datetime.now()
entity_id       = data.get('entity_id')
action 	        = data.get('action')
max             = data.get('max')
min             = data.get('min')
trigger_event   = data.get('trigger_event')
lvl             = None
elevation       = sun.attributes.get('elevation')

if min != None: dim = min
if max != None: bright = max

#get hour and minute from sun.next_midnight
def getMidnight (sun):
    time = sun.attributes.get('next_midnight')
    s1 = time.split('T')
    s2 = s1[1].split(':')
    return [int(s2[0]), int(s2[1])]

#Dim lights if between midnight and sunrise
midnight = getMidnight(sun)
shouldDim = 0
isPastMidnight = 0
if now.hour > midnight[0] or (now.hour == midnight[0] and now.minute >= midnight[1]):
    isPastMidnight = 1
if isPastMidnight == 1 and elevation < 5:
    shouldDim = 1

# Get current brightness value
s = entity_id.split('.')
type = s[0]
if type == 'light':
    ##Because i'm using light groups now, not real groups
    light = hass.states.get(entity_id)
    brightness = light.attributes.get('brightness') or 0
elif type == 'group':
    brightness = 0
    group = hass.states.get(entity_id)
    for i in group.attributes.get('entity_id'):
        light = hass.states.get(i)
        brightness = light.attributes.get('brightness') or 0
        if brightness > 0:
            break

# Parse actions for what to do
if action == 'dim_toggle':
    if light.state == 'off':  lvl = dim
    elif brightness >= 110: lvl = dim
    elif brightness < 110: lvl = bright

if action == 'dim':
    lvl = brightness/3
    if lvl < 30:
        lvl = 0

if action == 'toggle':
    if light.state == 'off' or brightness == 0: 
        lvl = bright
        if shouldDim == 1:
            lvl = nightBrightness
    elif light.state == 'on':
        lvl = 0

if action == 'dimmer':
    event_data = {}
    if trigger_event != None:
        split1 = trigger_event.split(' ')
        for i in split1:
            if (i == '<Event') or (i == 'cube_action[L]:') : continue
            split2 = i.split('=')
            event_data[split2[0]] = split2[1].rstrip(',').rstrip('>')

    lvl = brightness + float(event_data["action_value"])
    if lvl > maxBrightness:
        lvl = maxBrightness

if action == 'on':
    lvl = bright
    if shouldDim == 1:
        lvl = nightBrightness

if action == 'off':
    lvl = 0

logger.info(['entity_id', 'action', 'brightness', 'lvl', 'now.hour', 'now.minute', 'isPastMidnight', 'elevation', 'shouldDim', 'midnight'])
logger.info([entity_id, action, brightness, lvl, now.hour, now.minute, isPastMidnight, elevation, shouldDim, midnight])

# Call service
if int(lvl) <= 0:
    data = { "entity_id" : entity_id }
    hass.services.call('light', 'turn_off', data)
else:
    data = { "entity_id" : entity_id, "brightness" : lvl }
    hass.services.call('light', 'turn_on', data)
