PRAGMA foreign_keys=ON;

CREATE TABLE Programs (
    ProgramNumber INTEGER PRIMARY KEY AUTOINCREMENT,
    ProgramName VARCHAR(31) NOT NULL,
    PreferredProgramName VARCHAR(31),
    TimesRun INTEGER NOT NULL,
    TotalRunTime INTEGER NOT NULL,
    DisplayProgram INTEGER(1) NOT NULL,
    PreferredCommand VARCHAR(127),
    Likelihood REAL NOT NULL,
    Persistence INTEGER(1) NOT NULL
);

CREATE TABLE ProgramCommands (
    CommandNumber INTEGER PRIMARY KEY AUTOINCREMENT,
    ProgramCMD VARCHAR(127),
    ProgramNumber INTEGER NOT NULL,
    FOREIGN KEY(ProgramNumber) REFERENCES Programs(ProgramNumber)
);

CREATE TABLE ProgramLogs (
    LogNumber INTEGER PRIMARY KEY AUTOINCREMENT,
    ProgramNumber INTEGER NOT NULL,
    PID INTEGER(6) NOT NULL,
    DateTime INTEGER NOT NULL,
    OpenClose CHAR(5) NOT NULL,
    FOREIGN KEY(ProgramNumber) REFERENCES Programs(ProgramNumber)
);
