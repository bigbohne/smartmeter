use nom::{IResult, sequence::tuple, number::complete::{float, i32}, bytes::complete::{tag}, combinator::{fail, opt}};

#[derive(Debug, PartialEq)]
pub struct Obis {
    group1: i32,
    group2: i32,
    group3: i32,
    entry: Entry
}

#[derive(Debug, PartialEq)]
pub enum Unit {
    None,
    A,
    V,
    KW,
    Hz
}

#[derive(Debug, PartialEq)]
pub struct Entry {
    value: f32,
    unit: Unit
}

fn parse_unit(input: &str) -> IResult<&str, Unit> {
    match input {
        "V" => Ok(("", Unit::V)),
        "A" => Ok(("", Unit::A)),
        _ => fail(input)
    }
}

#[test]
fn test_parse_entry() {
    assert_eq!(parse_entry("227.8*V"), Ok(("", Entry{value: 227.8, unit: Unit::V})));
    assert_eq!(parse_entry("12345"), Ok(("", Entry{value: 12345.0, unit: Unit::None})));
}

pub fn parse_entry(input: &str) -> IResult<&str, Entry> {
    let value = float(input)?;
    let seperator = opt(tag("*"))(value.0)?;

    if let Some(_) = seperator.1 {
        let unit = parse_unit(seperator.0)?;
        Ok((unit.0, Entry{value: value.1, unit: unit.1}))
    } else {
        Ok((seperator.0, Entry{value: value.1, unit: Unit::None}))
    }
}