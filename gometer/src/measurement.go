package main

type Measurement struct {
	power_all_phases float32
	power_l1         float32
	power_l2         float32
	power_l3         float32

	energy_total    float32
	energy_forward  float32
	energy_backward float32

	grid_frequency float32
}
