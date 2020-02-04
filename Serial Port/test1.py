import pprint

data = {"sensor_1": {"id": 197000004, "name": "RELAY_OUTPUT_2_SPDT_OR_4_SPST", "RF_signal": "VERY GOOD", "relay_status1": 0, "realy_status2": 0}, "sensor_2": {"id": 691900001, "name": "SOIL_MOISTURE_SENSOR_WITH_I2C_OUTPUT", "value": 2.3, "temp_of_EC": 28.5,
                                                                                                                                                        "RF_signal": "VERY GOOD", "battery": "Full Battery"}, "sensor_3": {"id": 421900003, "name": "AMBIENT_HUMIDITY_SENSOR", "value": 44.427490234375, "temp_of_EC": 26.49749755859375, "RF_signal": "VERY GOOD", "battery": "Full Battery"}, "time": "10:8:30"}
# print(data)
pprint.pprint(data)
