x = 3 + 4
# Testing parsing unusual spacing
 y    =x  +7

# This shouldn't update the 'y' in the global scope
# Although it probably should eventually, because we should separate declarations from assignments
{ y = 100 }

{
	z = 2

	axolotl = 28 - (4 + z)
	y * axolotl
}
