CREATE DATABASE FestivalSafety;

USE FestivalSafety;

-- =====================================
-- USERS
-- =====================================

CREATE TABLE Users (

    ID INT AUTO_INCREMENT PRIMARY KEY,

    Name VARCHAR(100) NOT NULL,

    DOB DATE,

    Gender VARCHAR(20),

    Phone VARCHAR(30)
);

-- =====================================
-- ZONES
-- =====================================

CREATE TABLE Zones (

    ID INT AUTO_INCREMENT PRIMARY KEY,

    Name VARCHAR(100) NOT NULL,

    Capacity INT NOT NULL,

    Color VARCHAR(30)
);

-- =====================================
-- EMERGENCY MESSAGES
-- =====================================

CREATE TABLE EmergencyMessage (

    ID INT AUTO_INCREMENT PRIMARY KEY,

    Message TEXT NOT NULL,

    CreatedAT DATETIME DEFAULT CURRENT_TIMESTAMP,

    ZoneID INT,

    SenderUserID INT,

    FOREIGN KEY (ZoneID)
        REFERENCES Zones(ID),

    FOREIGN KEY (SenderUserID)
        REFERENCES Users(ID)
);

-- =====================================
-- INSERT DEFAULT ZONES
-- =====================================

INSERT INTO Zones (Name, Capacity, Color)
VALUES
('MainStage', 100, 'Red'),
('FoodCourt', 70, 'Orange'),
('ChillZone', 40, 'Green'),
('Entrance', 50, 'Yellow');