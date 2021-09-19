# Notes

Maximum and minimum scene length


Higher intensity should be lower effect lengths with more effects per subscene

Cooldown on effects (or diminish return)

Effect curves that controls pitch, zoom, speed, size etc.

Effects that support a graph curve to follow can be separate. A random graph can then be generated
before calling the effect. The graph input can be a set of points to interpolate (linear, bilinear, etc).

## Config file

Detailed control of all effect lengths, power levels

## Effects to implement

* Face zoom
* Freeze/stutter
* Freeze/stutter with pitch shift
* Fast forward
* Rewind
* Distorted high volume (but not earrape)
* Big head
* Echo zoom in (like a pulse echo)
* Fisheye nose



* Sentence mixing
* The sauce (saas)

## Parameters

effect_length (controls average length of effects)
effect_cooldown_period (controls how long pauses between effects)
effect_range (controls how high/low effect powers can go in range 0-100) default 25-50
max_concurrent_effects
effect_rate - controls how often affects are applied 0-100 (100 = always effect, 0 = never, 50 = 50% of the time)

## Effect priority

Some effects can maybe only be applied sometimes (sentence mixing, faces) so they should have a higher priority during selection. Can be implemented using the `selection_score`