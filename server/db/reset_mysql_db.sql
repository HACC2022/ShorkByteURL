CREATE DATABASE IF NOT EXISTS url_compressor;
USE url_compressor;
DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
    user_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(25) NOT NULL,
    password VARCHAR(50) NOT NULL,
    first_name VARCHAR(256) NOT NULL,
    last_name VARCHAR(128) NOT NULL,
    department ENUM('DAGS', 'HDOA', 'AG', 'B&F', 'DBEDT', 'DCCA', 'DOD', 'DOE', 'DHHL', 'DOH', 'DHRD', 'DLIR', 'DLNR', 'DPS', 'DOT', 'ETS', 'OHA', 'OIP', 'GOV', 'DHS') NOT NULL,
    user_record_timestamp TIMESTAMP NOT NULL,
    user_type ENUM('unverified', 'verified', 'rejected', 'blocked', 'admin') NOT NULL,
    phone VARCHAR(10) NOT NULL,
    email VARCHAR(320) NOT NULL,
    PRIMARY KEY(user_id)
);
CREATE TABLE IF NOT EXISTS urls (
    url_id INT NOT NULL AUTO_INCREMENT,
    owner_id INT NOT NULL,
    requester_id INT NOT NULL,
    short_url VARCHAR(32) NOT NULL,
    orig_url VARCHAR(2048) NOT NULL,
    url_request_timestamp TIMESTAMP NOT NULL,
    status ENUM('new', 'pending', 'accepted', 'rejected') NOT NULL,
    PRIMARY KEY(url_id),
    FOREIGN KEY(owner_id) REFERENCES users(user_id),
    FOREIGN KEY(requester_id) REFERENCES users(user_id)
);

INSERT INTO users(username, password, first_name, last_name, department, user_record_timestamp, user_type, phone, email)
VALUES
    ('jsmith', 'Fdb0A7T1NYhFRTpM', 'John', 'Smith', 'DOE', '2022-10-28 14:03:13', 'unverified', '8088432256', 'jsmith@k12.hi.us'),
    ('waquiano', 'YJt1HqmQW2136rHP', 'William', 'Aquiano', 'GOV', '2022-10-23 12:53:07', 'verified', '8089314531', 'waquiano@governor.hawaii.gov'),
    ('mjdole', '6XTqFZeouf35TspB', 'Mary Jane', 'Dole', 'DHS', '2022-10-27 13:57:48', 'verified', '8084924753', 'mjdole@hawaii.gov'),
    ('tharrison', 'StbF0eLBDDvJFCO7', 'Timothy', 'Harrison', 'ETS', '2022-10-13 16:32:27', 'admin', '8086763488', 'tharrison@hawaii.gov'),
    ('jwilson', 'jBCO9KYEf8Ki5mRV', 'Jennifer', 'Wilson', 'DCCA', '2022-10-26 18:30:24', 'rejected', '8082148746', 'jwilson@dcca.hawaii.gov'),
    ('badmann', 'sneeky123','B@d', 'maNn', 'DOT', '2022-10-31 00:00:01', 'blocked', '1234567890', 'badmann@oops.gov');
INSERT INTO urls(owner_id, requester_id, short_url, orig_url, url_request_timestamp, status)
VALUES
    (3, 3, '/https-health-hawaii-gov', 'https://health.hawaii.gov/', '2022-10-28 06:29:01', 'rejected'),
    (3, 3, '/ZS8', 'https://www.cisa.gov/news/2022/10/03/cisa-kicks-cybersecurity-awareness-month', '2022-10-29 16:32:15', 'pending'),
    (4, 4, '/mysecurity', 'https://mysignins.microsoft.com/security-info', '2022-10-30 15:47:21', 'accepted'),
    (2, 4, '/gov-cyber-mo-2022', 'https://governor.hawaii.gov/wp-content/uploads/2022/10/Cybersecurity-Awareness-Month.pdf', '2022-10-30 20:54:10', 'new');