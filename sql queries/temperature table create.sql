/* Temperature table. Create table if and only if it does not exist */
IF EXISTS (
    SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = N'SB_temperature_events'
)
BEGIN
    DROP TABLE SB_temperature_events
END

CREATE TABLE SB_temperature_events (
    eventID VARCHAR(30) not null PRIMARY KEY,
    targetName VARCHAR(70) not null,
    temperatureValue FLOAT not null,
    datestamp VARCHAR(30) not null,
    sensorName VARCHAR(30) not null,
    descriptionText VARCHAR(30) not null
)
GO

