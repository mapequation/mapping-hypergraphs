use std::fs;
use std::str::FromStr;

#[derive(PartialEq)]
pub enum RandomWalk {
    Lazy,
    NonLazy,
}

impl ToString for RandomWalk {
    fn to_string(&self) -> String {
        String::from(match self {
            Self::Lazy => "lazy",
            Self::NonLazy => "non-lazy",
        })
    }
}

pub enum Representation {
    Bipartite(RandomWalk),
    Unipartite(RandomWalk),
    Multilayer(RandomWalk),
}

impl FromStr for Representation {
    type Err = &'static str;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        if !s.starts_with('-') {
            return Err("Invalid argument");
        }

        use RandomWalk::*;
        use Representation::*;

        match s {
            "-b" => Ok(Bipartite(Lazy)),
            "-B" => Ok(Bipartite(NonLazy)),
            "-u" => Ok(Unipartite(Lazy)),
            "-U" => Ok(Unipartite(NonLazy)),
            "-m" => Ok(Multilayer(Lazy)),
            "-M" => Ok(Multilayer(NonLazy)),
            _ => Err("No such representation"),
        }
    }
}

pub struct Config {
    pub file: String,
    pub representation: Representation,
    pub outfile: String,
}

impl Config {
    pub fn new(mut args: std::env::Args) -> Result<Config, &'static str> {
        args.next();

        let representation = match args.next() {
            Some(arg) => arg.parse()?,
            None => return Err("Missing representation"),
        };

        let file = match args.next() {
            Some(arg) => fs::read_to_string(arg).expect("Cannot open file"),
            None => return Err("Missing filename"),
        };

        let outfile = match args.next() {
            Some(arg) => arg,
            None => return Err("Missing outfile"),
        };

        Ok(Self {
            file,
            representation,
            outfile,
        })
    }
}
