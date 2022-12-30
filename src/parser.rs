use nom::{
    bytes::complete::tag,
    character::complete::digit1,
    combinator::{fail, map_res, opt},
    multi::separated_list1,
    number::complete::float,
    IResult,
};

#[derive(Debug, PartialEq)]
pub struct Obis {
    tag: Vec<i32>,
    entry: Entry,
}

#[derive(Debug, PartialEq)]
pub enum Unit {
    None,
    A,
    V,
    KW,
    Hz,
}

#[derive(Debug, PartialEq)]
pub struct Entry {
    value: f32,
    unit: Unit,
}

fn parse_unit(input: &str) -> IResult<&str, Unit> {
    match input {
        "V" => Ok(("", Unit::V)),
        "A" => Ok(("", Unit::A)),
        _ => fail(input),
    }
}

#[test]
fn test_parse_entry() {
    assert_eq!(
        parse_entry("227.8*V"),
        Ok((
            "",
            Entry {
                value: 227.8,
                unit: Unit::V
            }
        ))
    );
    assert_eq!(
        parse_entry("12345"),
        Ok((
            "",
            Entry {
                value: 12345.0,
                unit: Unit::None
            }
        ))
    );
}

pub fn parse_entry(input: &str) -> IResult<&str, Entry> {
    let value = float(input)?;
    let seperator = opt(tag("*"))(value.0)?;

    if seperator.1.is_some() {
        let unit = parse_unit(seperator.0)?;
        Ok((
            unit.0,
            Entry {
                value: value.1,
                unit: unit.1,
            },
        ))
    } else {
        Ok((
            seperator.0,
            Entry {
                value: value.1,
                unit: Unit::None,
            },
        ))
    }
}

#[test]
fn test_parse_tag() {
    assert_eq!(parse_tag("3.2.1"), Ok(("", vec![3, 2, 1])));
    assert_eq!(parse_tag("1.18"), Ok(("", vec![1, 18])));
}

pub fn parse_tag(input: &str) -> IResult<&str, Vec<i32>> {
    let tag: (&str, Vec<i32>) = separated_list1(tag("."), map_res(digit1, str::parse))(input)?;

    if tag.1.len() > 3 || tag.1.len() < 2 {
        fail::<_, Vec<i32>, _>(input)?;
    }

    Ok((tag.0, tag.1))
}