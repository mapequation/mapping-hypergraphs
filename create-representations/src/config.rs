use std::path::PathBuf;

pub struct Config {
    pub file: PathBuf,
}

impl Config {
    pub fn new(mut args: std::env::Args) -> Result<Config, &'static str> {
        args.next();

        let file = match args.next() {
            Some(arg) => arg.into(),
            None => return Err("missing filename"),
        };

        Ok(Self { file })
    }
}
