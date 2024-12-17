package main

import (
	"log"
	"maps"
	"time"

	"github.com/alecthomas/kingpin/v2"
)

var (
	metertype = kingpin.Flag("type", "Type of Smartmeter [\"modbustcp\"]").Required().Envar("GOMETER_TYPE").String()
	interval  = kingpin.Flag("interval", "Interval of measurements in seconds").Default("15").Int()
	mqtturl   = kingpin.Flag("mqtt", "URL of MQTT Server").String()
	modbusurl = kingpin.Flag("modbus", "Modbus Address of the Smartmeter").String()
)

func main() {
	kingpin.Parse()

	data1, _ := readObisMeter("192.168.2.247:23", "/?!\r\n")
	data2, _ := readObisMeter("192.168.2.247:23", "/2!\r\n")
	maps.Copy(data1, data2)

	log.Println(data1)
	return

	var ticker = time.NewTicker(time.Second * time.Duration(*interval))

	var mqttclient, err = CreateMQTTClient(MQTTClientParams{
		name: "boffi_office",
		url:  *mqtturl,
	})

	if err != nil {
		log.Fatalln(err)
	}

	for {
		<-ticker.C

		var measurement, err = readModbusMeter(ModbusParameters{
			url: *modbusurl,
		})

		if err != nil {
			log.Fatal(err)
		}

		log.Println(measurement)
		mqttclient.Publish(measurement)
	}

}
