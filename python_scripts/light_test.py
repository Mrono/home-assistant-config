""" Brighten a light, then return to previous brightness state """ 

#from datetime import datetime, time

#now = datetime.now()
#now_time = now.time()

# Get Params
entity_id  = data.get('entity_id')
action 	   = data.get('action')
max        = data.get('max')
min        = data.get('min')
trigger_event    = data.get('trigger_event')

event_data = {}
if trigger_event != None:
    split1 = trigger_event.split(' ')
    for i in split1:
        if (i == '<Event') or (i == 'cube_action[L]:') : continue
        split2 = i.split('=')
        event_data[split2[0]] = split2[1].rstrip(',').rstrip('>')

#sunrise = hass.states.get('sun.sun').attributes.get('next_rising')

dim = 50
bright = 255
lvl = None

if min != None: dim = min
if max != None: bright = max

# Get current brightness value
group     = hass.states.get(entity_id)
light = hass.states.get(group.attributes.get('entity_id')[0])
brightness = light.attributes.get('brightness') or 0

if action == 'dim_toggle':
    if group.state == 'off':  lvl = dim
    elif brightness >= 110: lvl = dim
    elif brightness < 110: lvl = bright

if action == 'toggle':
    if group.state == 'off': 
#TODO time based brightness
        lvl = bright
    elif group.state == 'on':
        lvl = 0

if action == 'dimmer':
    lvl = brightness + float(event_data["action_value"])
    if lvl > 255:
        lvl = 255

# Call service
if lvl == 0 :
	data = { "entity_id" : entity_id }
	hass.services.call('light', 'turn_off', data)
else :
	data = { "entity_id" : entity_id, "brightness" : lvl }
	hass.services.call('light', 'turn_on', data)
