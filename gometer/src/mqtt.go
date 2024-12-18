package main

import (
	"fmt"

	mqtt "github.com/eclipse/paho.mqtt.golang"
)

type MQTTClient struct {
	client mqtt.Client
	name   string
}

type MQTTClientParams struct {
	name string
	url  string
}

func CreateMQTTClient(params MQTTClientParams) (mqttclient *MQTTClient, err error) {
	var will_topic = fmt.Sprintf("smartmeter/%s/connected", params.name)
	var options = mqtt.NewClientOptions().AddBroker(params.url).SetClientID(fmt.Sprintf("gometer-%s", params.name)).SetWill(will_topic, "0", 0, false)
	var client = mqtt.NewClient(options)
	var t = client.Connect()
	if t.Wait() && t.Error() != nil {
		return nil, t.Error()
	}

	t = client.Publish(will_topic, 0, false, "1")
	if t.Wait() && t.Error() != nil {
		return nil, t.Error()
	}

	mqttclient = &MQTTClient{}

	mqttclient.client = client
	mqttclient.name = params.name

	return mqttclient, nil
}

func (c *MQTTClient) Publish(measurement *Measurement) {
	c.client.Publish(fmt.Sprintf("smartmeter/%s/power/Total", c.name), 0, false, fmt.Sprint(measurement.power_all_phases))
	c.client.Publish(fmt.Sprintf("smartmeter/%s/power/L1", c.name), 0, false, fmt.Sprint(measurement.power_l1))
	c.client.Publish(fmt.Sprintf("smartmeter/%s/power/L2", c.name), 0, false, fmt.Sprint(measurement.power_l2))
	c.client.Publish(fmt.Sprintf("smartmeter/%s/power/L3", c.name), 0, false, fmt.Sprint(measurement.power_l3))

	for k, v := range measurement.counter {
		c.client.Publish(fmt.Sprintf("smartmeter/%s/counter/%s", k, c.name), 0, false, fmt.Sprint(v))
	}

	c.client.Publish(fmt.Sprintf("smartmeter/%s/frequency", c.name), 0, false, fmt.Sprint(measurement.grid_frequency))
}
