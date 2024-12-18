package main

import (
	"errors"
)

type Measurement struct {
	power_all_phases float32
	power_l1         float32
	power_l2         float32
	power_l3         float32

	counter map[string]float32

	grid_frequency float32
}

type MeasurementSettings struct {
	metertype string
	url       string
}

func createMeasurement(settings MeasurementSettings) (*Measurement, error) {
	if settings.metertype == "modbustcp" {
		return readModbusMeter(ModbusParameters{url: settings.url})
	}

	if settings.metertype == "iec62056" {
		return readObisMeter(settings)
	}

	return nil, errors.New("unsupported meter type")
}
