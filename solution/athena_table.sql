CREATE EXTERNAL TABLE IF NOT EXISTS HVAC.thermafuser_reading (
  `record_timestamp` timestamp,
  `room_occupancy` boolean,
  `zone_temp` float,
  `supply_air` float,
  `air_flw_fdbck` float,
  `occ_cool_stpn` float,
  `occ_heat_stpn` float
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = ',',
  'field.delim' = ','
) LOCATION 's3://factory1-machine1-david-laredo-test/'
TBLPROPERTIES ('has_encrypted_data'='false');


SELECT * FROM thermafuser WHERE thermafuser.timestamp BETWEEN timestamp '2021-02-17' AND timestamp '2021-02-18';