nightBrightness = 25
maxBrightness   = 255
dim             = 50
bright          = maxBrightness




now             = datetime.datetime.now()
entity_id       = data.get('entity_id')
action 	        = data.get('action')
max             = data.get('max')
min             = data.get('min')
trigger_event   = data.get('trigger_event')
lvl             = None

if min != None: dim = min
if max != None: bright = max

#Dim lights if between midnight and sunrise
shouldDim = 0
elevation = hass.states.get('sun.sun').attributes.get('elevation')
if now.hour < 9 and elevation < 0:
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
    if group.state == 'off':  lvl = dim
    elif brightness >= 110: lvl = dim
    elif brightness < 110: lvl = bright

if action == 'toggle':
    if group.state == 'off': 
        lvl = bright
        if shouldDim == 1:
            lvl = nightBrightness
    elif group.state == 'on':
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

# Call service
if lvl == 0:
    data = { "entity_id" : entity_id }
    hass.services.call('light', 'turn_off', data)
else:
    data = { "entity_id" : entity_id, "brightness" : lvl }
    hass.services.call('light', 'turn_on', data)
