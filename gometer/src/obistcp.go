package main

import (
	"bufio"
	"errors"
	"log"
	"maps"
	"net"
	"net/url"
	"regexp"
	"strconv"
	"strings"
	"time"
)

type ObisValues map[string]float64

func readObisMeter(settings MeasurementSettings) (*Measurement, error) {
	parsedUrl, err := url.ParseRequestURI(settings.url)
	if err != nil {
		return nil, err
	}

	data1, _ := readObisMeterInternal(parsedUrl.Host, "/?!\r\n")
	data2, _ := readObisMeterInternal(parsedUrl.Host, "/2!\r\n")
	maps.Copy(data1, data2)

	log.Println(data1)
	return nil, errors.ErrUnsupported
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
		log.Println(line)

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

		data[obis] = value
	}

	return data, nil
}
