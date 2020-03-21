from device_selector.device import Device

transmission_time = 4.0  # How much time it takes to transmit (in secs)
furthest_range = 15.0  # Maximal distance between devices for transmission (in degrees)


def pick_available(me: Device, others: [Device]):
	return list(filter(lambda d: d.distance_to(me) < furthest_range and
							d.distance_to_after(me, transmission_time) < furthest_range, others))
