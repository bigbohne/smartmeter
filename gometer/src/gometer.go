package main

import (
	"log"
	"time"

	"github.com/alecthomas/kingpin/v2"
)

var (
	metertype = kingpin.Flag("type", "Type of Smartmeter [\"modbustcp\"]").Required().Envar("GOMETER_TYPE").Strings()
	interval  = kingpin.Flag("interval", "Interval of measurements in seconds").Default("15").Int()
	ip        = kingpin.Flag("ip", "IP Address of Smartmeter").IP()
	port      = kingpin.Flag("port", "Port of the Smartmeter").Int16()
)

func main() {
	kingpin.Parse()

	var ticker = time.NewTicker(time.Second * time.Duration(*interval))

	var mqttclient, err = CreateMQTTClient(MQTTClientParams{
		name: "boffi_office",
	})

	if err != nil {
		log.Fatalln(err)
	}

	for {
		<-ticker.C

		var measurement, err = readModbusMeter(ModbusParameters{
			ip:   "192.168.2.232",
			port: 9999,
		})

		if err != nil {
			log.Fatal(err)
		}

		log.Println(measurement)
		mqttclient.Publish(measurement)
	}

}
