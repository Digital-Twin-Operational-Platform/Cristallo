Soton_twin_data = {
	'metadata': {
		'location': 'Southampton',
		'lastupdate': {
			'date': '26/05/2020',
			'time': '11:00'
		}
	},
	'structure': {
		'mass': {'value': 5.201, 'units': 'kg'},	# mass of each storey
		'elasticityModulus': {'value': 70e9, 'units': 'Pa'},
		'legWidth': {'value': 25e-3, 'units': 'm'},
		'legThickness': {'value': 3e-3, 'units': 'm'},
		'legLength': {'value': 153.3e-3, 'units': 'm'},
		'dampRatio': {'value': 0.2e-2, 'units': '-'},
		'floorCoordinates': {
			'part': ['ground', 'floor1', 'floor2', 'floor3'],
			'yCoordinate': {'value': [23.5e-3, 201.8e-3, 380.1e-3, 558.4e-3], 'units': 'm'}
		}
	},
	'primaryForce': {
		'locationFloor': 1,
		'sensorID': 'forceGaugeSN01',
		'variableName': 'fp',
		'units': 'N',
		'sensitivity': {'value': 11.2, 'units': 'mV/N'},
		'samplingFreq': {'value': 1e3, 'units': 'Hz'}
	},
	'response1': {
		'locationFloor': 1,
		'sensorID': 'accelerometerSN01',
		'variableName': 'ddotx1',
		'units': 'm/s^2',
		'sensitivity': {'value': 10.15, 'units': 'mV/ms-2'},
		'samplingFreq': {'value': 1e3, 'units': 'Hz'}
	},
	'response2': {
		'locationFloor': 2,
		'sensorID': 'accelerometerSN02',
		'variableName': 'ddotx2',
		'units': 'm/s^2',
		'sensitivity': {'value': 10.17, 'units': 'mV/ms-2'},
		'samplingFreq': {'value': 1e3, 'units': 'Hz'}
	},
	'response3': {
		'locationFloor': 3,
		'sensorID': 'accelerometerSN03',
		'variableName': 'ddotx3',
		'units': 'm/s^2',
		'sensitivity': {'value': 10.26, 'units': 'mV/ms-2'},
		'samplingFreq': {'value': 1e3, 'units': 'Hz'}
	}
}