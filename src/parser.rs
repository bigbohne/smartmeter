use pest::Parser;

#[derive(Parser)]
#[grammar = "response.pest"]
pub struct ResponseParser;

#[test]
fn test_parser() {
    assert_eq!(
        parse_obis("32.7.0(227.8*V)"),
        Some(ObisLine {
            tag: "32.7.0".to_string(),
            value: 227.8,
            unit: "V".to_string()
        })
    )
}

#[derive(PartialEq, Debug)]
pub struct ObisLine {
    tag: String,
    value: f64,
    unit: String,
}

pub fn parse_obis(input: &str) -> Option<ObisLine> {
    let result = ResponseParser::parse(Rule::obis_line, input)
        .unwrap()
        .next()
        .unwrap();

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

    Some(ObisLine {
        tag: tag,
        value: value,
        unit: unit,
    })
}
