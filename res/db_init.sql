CREATE TABLE `trips` (
  `id` bigserial PRIMARY KEY,
  `subscriber_type` VARCHAR,
  `bikeid` VARCHAR,
  `start_time` DATE,
  `start_station_id` bigserial,
  `start_station_name` VARCHAR,
  `end_station_id` bigserial,
  `end_station_name` VARCHAR,
  `duration_minutes` INT
);

CREATE TABLE `stations` (
  `station_id` bigserial PRIMARY KEY,
  `name` VARCHAR,
  `status` VARCHAR,
  `address` VARCHAR,
  `alternate_name` VARCHAR,
  `city_asset_number` INT,
  `property_type` VARCHAR,
  `number_of_docks` INT,
  `power_type` VARCHAR,
  `footprint_length` float,
  `footprint_width` float,
  `notes` VARCHAR,
  `council_district` INT,
  `modified_date` DATE
);

ALTER TABLE `trips` ADD FOREIGN KEY (`start_station_id`) REFERENCES `stations` (`station_id`);

ALTER TABLE `trips` ADD FOREIGN KEY (`end_station_id`) REFERENCES `stations` (`station_id`);

CREATE INDEX `trips_index_0` ON `trips` (`bikeid`);

CREATE INDEX `stations_index_1` ON `stations` (`city_asset_number`);
