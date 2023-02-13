mod parser;

extern crate pest;
#[macro_use]
extern crate pest_derive;

use bytes::{BufMut, BytesMut};
use std::fs::File;
use std::io::prelude::*;

fn main() {
    let mut buffer = BytesMut::with_capacity(1024);

    let file = File::open("data/capture.txt").unwrap();

    let mut capture = false;
    for byte_result in file.bytes() {
        let byte = byte_result.unwrap();

        if byte == 0x02 {
            // STX
            capture = true;
            continue;
        }

        if byte == 0x03 {
            // ETX
            break;
        }

        if capture {
            buffer.put_u8(byte); // Append next byte to buffer
        }
    }

    println!("buffer: {:?}", &buffer);
}
