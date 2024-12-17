package main

import (
	"time"

	"github.com/simonvetter/modbus"
)

type ModbusParameters struct {
	url string
}

func readModbusMeter(params ModbusParameters) (measurement Measurement, err error) {
	var client *modbus.ModbusClient

	client, err = modbus.NewClient(&modbus.ClientConfiguration{
		URL:     params.url,
		Timeout: 1 * time.Second,
	})

	if err != nil {
		return
	}

	err = client.Open()
	if err != nil {
		return
	}

	err = client.SetEncoding(modbus.BIG_ENDIAN, modbus.HIGH_WORD_FIRST)
	if err != nil {
		return
	}

	measurement.power_all_phases, err = client.ReadFloat32(0x1c, modbus.HOLDING_REGISTER)
	if err != nil {
		return
	}

	measurement.power_l1, err = client.ReadFloat32(0x1e, modbus.HOLDING_REGISTER)
	if err != nil {
		return
	}

	measurement.power_l2, err = client.ReadFloat32(0x20, modbus.HOLDING_REGISTER)
	if err != nil {
		return
	}

	measurement.power_l3, err = client.ReadFloat32(0x22, modbus.HOLDING_REGISTER)
	if err != nil {
		return
	}

	measurement.energy_total, err = client.ReadFloat32(0x100, modbus.HOLDING_REGISTER)
	if err != nil {
		return
	}

	measurement.energy_forward, err = client.ReadFloat32(0x108, modbus.HOLDING_REGISTER)
	if err != nil {
		return
	}

	measurement.energy_backward, err = client.ReadFloat32(0x110, modbus.HOLDING_REGISTER)
	if err != nil {
		return
	}

	measurement.grid_frequency, err = client.ReadFloat32(0x14, modbus.HOLDING_REGISTER)
	if err != nil {
		return
	}

	client.Close()

	return
}
