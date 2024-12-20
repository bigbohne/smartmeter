package main

import (
	"bufio"
	"log"
	"maps"
	"net"
	"net/url"
	"regexp"
	"strconv"
	"strings"
	"time"
)

type ObisValues map[string]float32

func readObisMeter(settings MeasurementSettings) (*Measurement, error) {
	parsedUrl, err := url.ParseRequestURI(settings.url)
	if err != nil {
		return nil, err
	}

	data1, err := readObisMeterInternal(parsedUrl.Host, "/?!\r\n")
	if err != nil {
		return nil, err
	}

	data2, err := readObisMeterInternal(parsedUrl.Host, "/2!\r\n")
	if err != nil {
		return nil, err
	}

	measurement, _ := createObisMeasurement(data1, data2)

	return measurement, nil
}

func createObisMeasurement(data1 ObisValues, data2 ObisValues) (*Measurement, error) {
	maps.Copy(data1, data2)

	measurement := &Measurement{}

	measurement.power_all_phases = data1["1.7.0"]
	measurement.power_l1 = data1["21.7.0"]
	measurement.power_l2 = data1["41.7.0"]
	measurement.power_l3 = data1["61.7.0"]
	measurement.grid_frequency = data1["34.7"]

	measurement.counter = make(map[string]float32)
	measurement.counter["1.8.0"] = data1["1.8.0"]
	measurement.counter["1.8.1"] = data1["1.8.1"]
	measurement.counter["1.8.2"] = data1["1.8.2"]

	return measurement, nil
}

func readObisMeterInternal(ipport string, command string) (ObisValues, error) {
	conn, err1 := net.Dial("tcp", ipport)
	if err1 != nil {
		return nil, err1
	}

	defer conn.Close()

	reader := bufio.NewReader(conn)

	conn.Write([]byte(command))

	_, err2 := reader.ReadString(byte('\n'))
	if err2 != nil {
		return nil, err2
	}

	conn.Write([]byte("\x06050\r\n"))

	conn.SetReadDeadline(time.Now().Add(15 * time.Second))

	reg, err3 := regexp.Compile(`(?mi)^([0-9\.]+\*?[0-9]*)\(([0-9\.]+).*\)`)
	if err3 != nil {
		return nil, err3
	}

	data := make(ObisValues)

	for true {
		line, err2 := reader.ReadString(byte('\n'))
		if err2 != nil {
			log.Fatalln(err2)
		}

		line = strings.TrimSpace(line)
		//log.Println(line)

		if line[0] == '!' {
			break
		}

		submatches := reg.FindAllStringSubmatch(line, -1)
		if len(submatches) != 1 {
			continue
		}

		findings := submatches[0]

		if len(findings) != 3 {
			continue
		}

		obis := findings[1]
		value, _ := strconv.ParseFloat(findings[2], 64)

		data[obis] = float32(value)
	}

	return data, nil
}
