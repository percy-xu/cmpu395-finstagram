DROP TABLE IF EXISTS Person;
DROP TABLE IF EXISTS Photo;
DROP TABLE IF EXISTS FriendGroup;
DROP TABLE IF EXISTS ReactTo;
DROP TABLE IF EXISTS Tag;
DROP TABLE IF EXISTS SharedWith;
DROP TABLE IF EXISTS BelongTo;
DROP TABLE IF EXISTS Follow;

CREATE TABLE Person (
        username VARCHAR(32),
        password VARCHAR(64),
        firstName VARCHAR(32),
        lastName VARCHAR(32),
        email VARCHAR(32),
        PRIMARY KEY (username)
);

CREATE TABLE Photo (
        pID INT AUTO_INCREMENT,
        postingDate DATETIME,
        filePath VARCHAR(255), -- you may replace this by a BLOB attribute to store the actual photo
        allFollowers INT,
        caption VARCHAR(1000),
        poster VARCHAR(32),
        PRIMARY KEY (pID),
        FOREIGN KEY (poster) REFERENCES Person (username)
);

CREATE TABLE FriendGroup (
        groupName VARCHAR(32),
        groupCreator VARCHAR(32),
        description VARCHAR(1000),
        PRIMARY KEY (groupName, groupCreator),
        FOREIGN KEY (groupCreator) REFERENCES Person (username)
);

CREATE TABLE ReactTo (
        username VARCHAR(32),
        pID INT,
        reactionTime DATETIME,
        comment VARCHAR(1000),
        emoji VARCHAR(32), -- you may replace this by a BLOB or fileName of a jpg or some such
	PRIMARY KEY (username, pID),
        FOREIGN KEY (pID) REFERENCES Photo (pID),
        FOREIGN KEY (username) REFERENCES Person (username)
);

CREATE TABLE Tag (
        pID INT,
        username VARCHAR(32),
        tagStatus INT,
	PRIMARY KEY (pID, username),
        FOREIGN KEY (pID) REFERENCES Photo (pID),
        FOREIGN KEY (username) REFERENCES Person (username)
);

CREATE TABLE SharedWith (
        pID INT,
        groupName VARCHAR(32),
        groupCreator VARCHAR(32),
	PRIMARY KEY (pID, groupName, groupCreator),
	FOREIGN KEY (groupName, groupCreator) REFERENCES FriendGroup(groupName, groupCreator),
        FOREIGN KEY (pID) REFERENCES Photo (pID)
);

CREATE TABLE BelongTo (
        username VARCHAR(32),
        groupName VARCHAR(32),
	groupCreator VARCHAR(32),
        PRIMARY KEY (username, groupName, groupCreator),
        FOREIGN KEY (username) REFERENCES Person (username),
        FOREIGN KEY (groupName, groupCreator) REFERENCES FriendGroup (groupName, groupCreator)
);

CREATE TABLE Follow (
        follower VARCHAR(32),
        followee VARCHAR(32),
        followStatus INT,
        PRIMARY KEY (follower, followee),
        FOREIGN KEY (follower) REFERENCES Person (username),
        FOREIGN KEY (followee) REFERENCES Person (username)
);

-- INSERT INTO Person (username, password, firstName, lastName, email) VALUES
-- ('A', 'A', 'Ann', 'Andrews', 'ann123@gmail.com'),
-- ('B', 'B', 'Bill', 'Barker', 'washyourhands@hotmail.com'),
-- ('C', 'C', 'Cathy', 'Chen', 'ilovedatabases@gmail.com'),
-- ('D', 'D', 'Dave', 'Davis', 'davedavis1@gmail.com'),
-- ('E', 'E', 'Emily', 'Elhaj', 'stayhomestaysafe@aol.com');

-- INSERT INTO Photo (pID, postingdate, filepath, allFollowers, caption, poster) VALUES
-- (1, '2020-01-01 00:00:00', '1.jpg', 1, 'photo 1', 'A'),
-- (2, '2020-02-02 00:00:00', '2.jpg', 1, 'photo 2', 'C'),
-- (3, '2020-1-11 00:00:00', '3.jpg', 1, 'photo 3', 'D'),
-- (4, '2020-2-11 00:00:00', '4.jpg', 1, NULL, 'D'),
-- (5, '2020-3-11 00:00:00', '5.jpg', 0, 'photo 5', 'E');

-- INSERT INTO FriendGroup (groupName, groupCreator, description) VALUES
-- ('best friends', 'E', 'Emily: best friends'),
-- ('best friends', 'D', 'Dave: best friends'),
-- ('roommates', 'D', 'Dave: roommates');

-- INSERT INTO BelongTo (username, groupName, groupCreator) VALUES
-- ('E', 'best friends', 'E'),
-- ('D', 'best friends', 'D'),
-- ('D', 'roommates', 'D'),
-- ('A', 'best friends', 'E'),
-- ('B', 'roommates', 'D');

-- INSERT INTO Follow (follower, followee, followStatus) VALUES
-- ('B', 'A', 1),
-- ('C', 'A', 1),
-- ('D', 'A', 0),
-- ('B', 'D', 1),
-- ('A', 'B', 1),
-- ('E', 'A', 1),
-- ('D', 'B', 1),
-- ('E', 'B', 0),
-- ('D', 'C', 1),
-- ('A', 'E', 1);

-- INSERT INTO Tag (pID, username, tagStatus) VALUES
-- (1, 'B', 0),
-- (1, 'C', 1),
-- (2, 'D', 1),
-- (1, 'E', 1);

-- INSERT INTO ReactTo (username, pID, reactionTime, comment, emoji) VALUES
-- ('D', 2, '2022-04-23 00:00:00', 'nice photo!', 'heart'),
-- ('E', 1, '2022-04-23 00:00:00', NULL, 'thumbs up');

-- INSERT INTO SharedWith (pID, groupName, groupCreator) VALUES
-- (5, 'best friends', 'E'),
-- (3, 'best friends', 'D');