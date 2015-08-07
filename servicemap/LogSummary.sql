CREATE TABLE LogSummary (
id int not null auto_increment,
srcip varchar(15) NOT NULL,
dstip varchar(15) NOT NULL,
proto varchar(3) NOT NULL,
srcport smallint NOT NULL,
dstport smallint NOT NULL,
counter int not null,
lastseen datetime not null,
firstseen datetime not null,
primary key (id),
UNIQUE connection_entry (`srcip`,`dstip`,`proto`,`dstport`)
);
