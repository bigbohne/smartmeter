use pest::Parser;

#[derive(Parser)]
#[grammar = "response.pest"]
pub struct ResponseParser;

#[test]
fn test_parser() {
    assert_eq!(
        parse_obis("32.7.0(227.8*V)"),
        Ok(ObisLine {
            tag: "32.7.0".to_string(),
            value: 227.8,
            unit: "V".to_string()
        })
    );

    assert_eq!(
        parse_obis("32.7(227567)"),
        Ok(ObisLine {
            tag: "32.7".to_string(),
            value: 227567.0,
            unit: "".to_string()
        })
    );

    assert_eq!(parse_obis("abc(227.8)"), Err(ParserError::General));
}

#[derive(PartialEq, Debug)]
pub struct ObisLine {
    tag: String,
    value: f64,
    unit: String,
}

#[derive(Debug, PartialEq)]
pub enum ParserError {
    General,
}

pub fn parse_obis(input: &str) -> Result<ObisLine, ParserError> {
    let result = ResponseParser::parse(Rule::obis_line, input)
        .or(Err(ParserError::General))?
        .next()
        .ok_or(ParserError::General)?;

    let mut tag: String = String::default();
    let mut value: f64 = 0.0;
    let mut unit: String = String::default();

    for entry in result.into_inner() {
        match entry.as_rule() {
            Rule::tag => {
                tag = String::from(entry.as_str());
            }
            Rule::value => {
                for value_pair in entry.into_inner() {
                    match value_pair.as_rule() {
                        Rule::number => value = value_pair.as_str().parse::<f64>().unwrap(),
                        Rule::unit => unit = String::from(value_pair.as_str()),
                        _ => unreachable!(),
                    }
                }
            }
            _ => unreachable!(),
        }
    }

    Ok(ObisLine {
        tag: tag,
        value: value,
        unit: unit,
    })
}
