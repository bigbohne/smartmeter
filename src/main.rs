use bytes::{BytesMut, BufMut, Buf};
use std::io::prelude::*;
use std::fs::File;

fn parse_signin_response(response: &[u8]) {
    
}

fn main() {
    let mut buffer = BytesMut::with_capacity(1024);

    let file = File::open("data/capture.txt").unwrap();

    for byte_result in file.bytes() {
        let byte = byte_result.unwrap();

        buffer.put_u8(byte); // Append next byte to buffer
        
    }

    println!("Hello, world!");
}
