mod parser;

extern crate pest;
#[macro_use]
extern crate pest_derive;

use bytes::BytesMut;

use serial2::SerialPort;
use std::io::prelude::*;

fn main() {
    let mut buffer = BytesMut::with_capacity(1024);

    let mut port = SerialPort::open("/dev/ttyS0", 115200).unwrap();
    let mut config = port.get_configuration().unwrap();
    config.set_char_size(serial2::CharSize::Bits7);
    config.set_parity(serial2::Parity::Even);
    config.set_stop_bits(serial2::StopBits::One);
    port.set_configuration(&config).unwrap();

    port.write("/?!\r\n".as_bytes());
}
