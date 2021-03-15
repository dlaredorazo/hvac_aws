from sqlalchemy import Column, Integer, String, Table, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, class_mapper
from datetime import datetime

Base = declarative_base()


def copy_sqla_object(obj, omit_fk=True):
	"""Given an SQLAlchemy object, creates a new object (FOR WHICH THE OBJECT
	MUST SUPPORT CREATION USING __init__() WITH NO PARAMETERS), and copies
	across all attributes, omitting PKs, FKs (by default), and relationship
	attributes."""
	cls = type(obj)
	mapper = class_mapper(cls)
	newobj = cls()  # not: cls.__new__(cls)
	pk_keys = set([c.key for c in mapper.primary_key])
	rel_keys = set([c.key for c in mapper.relationships])
	prohibited = pk_keys | rel_keys
	if omit_fk:
		fk_keys = set([c.key for c in mapper.columns if c.foreign_keys])
		prohibited = prohibited | fk_keys
	for k in [p.key for p in mapper.iterate_properties if p.key not in prohibited]:
		try:
			value = getattr(obj, k)
			setattr(newobj, k, value)
		except AttributeError:
			pass
	return newobj



class DataPoint(Base):
	"""Class to map to the DataPoints table in the HVAC DB"""

	__tablename__ = 'datapoints'

	_path = Column('Path', String(255), primary_key = True)
	_server = Column('Server', String(255))
	_location = Column('Location', String(255))
	_branch = Column('Branch', String(255))
	_subBranch = Column('SubBranch', String(255))
	_controlProgram = Column('ControlProgram', String(255))
	_point = Column('Point', String(255))
	_zone = Column('Zone', String(255))
	_bacnetAddress = Column('BacnetAddress', String(255))
	_bacnetDevId = Column('BacnetDevId', Integer)
	_bacnetObjectType = Column('BacnetObjectType', String(255))
	_pointType = Column('PointType', Integer)
	_componentId = Column('ComponentId', Integer)
	_pathMappingId = Column('PathMappingsId', Integer, ForeignKey("pathmappings.Id"))

	#PathMapping relationship
	_pathMapping = relationship("PathMapping", back_populates = "_dataPoints")

	#Constructor

	def __init__(self, path, server, location, branch, subBranch, controlProgram, point, zone,
		bacnetAddress, bacnetDevId, bacnetObjectType, pointType, componentId = None, pathMappingId = None, pathMapping = None):

		self._path = path
		self._server = server
		self._location = location
		self._branch = branch
		self._subBranch = subBranch
		self._controlProgram = controlProgram
		self._point = point
		self._zone = zone
		self._bacnetAddress = bacnetAddress
		self._bacnetDevId = bacnetDevId
		self._bacnetObjectType = bacnetObjectType
		self._pointType = pointType
		self._componentId = componentId
		self._pathMappingId = pathMappingId
		self._pathMapping = pathMapping

	#Properties

	@property
	def path(self):
		return self._path

	@path.setter
	def path(self, value):
		self._path = value

	@property
	def server(self):
		return self._server

	@server.setter
	def server(self, value):
		self._server = value

	@property
	def location(self):
		return self._location

	@location.setter
	def location(self, value):
		self._location = value

	@property
	def branch(self):
		return self._branch

	@branch.setter
	def branch(self, value):
		self._branch = value

	@property
	def subBranch(self):
		return self._subBranch

	@subBranch.setter
	def subBranch(self, value):
		self._subBranch = value

	@property
	def controlProgram(self):
		return self._controlProgram

	@controlProgram.setter
	def controlProgram(self, value):
		self._controlProgram = value

	@property
	def point(self):
		return self._point

	@point.setter
	def point(self, value):
		self._point = value

	@property
	def zone(self):
		return self._zone

	@zone.setter
	def zone(self, value):
		self._zone = value

	@property
	def bacnetAddress(self):
		return self._bacnetAddress

	@bacnetAddress.setter
	def bacnetAddress(self, value):
		self._bacnetAddress = value

	@property
	def bacnetDevId(self):
		return self._bacnetDevId

	@bacnetDevId.setter
	def bacnetDevId(self, value):
		self._bacnetDevId = value

	@property
	def bacnetObjectType(self):
		return self._bacnetObjectType

	@bacnetObjectType.setter
	def bacnetObjectType(self, value):
		self._bacnetObjectType = value

	@property
	def componentId(self):
		return self._componentId

	@componentId.setter
	def componentId(self, value):
		self._componentId = value

	@property
	def pointType(self):
		return self._pointType

	@pointType.setter
	def pointType(self, value):
		self._pointType = value

	@property
	def pathMappingId(self):
		return self._pathMappingId

	@pathMappingId.setter
	def pathMappingId(self, value):
		self._pathMappingId = value

	@property
	def pathMapping(self):
		return self._pathMapping

	@pathMapping.setter
	def pathMapping(self, value):
		self._pathMapping = value

	def __str__(self):
		return "<DataPoint(path = '%s', server = '%s', location = '%s', branch = '%s', subBranch = '%s', controlProgram = '%s', point = '%s',\
		 zone = '%s', bacnetAddress = '%s', bacnetDevId = '%s', bacnetObjectType = '%s', pointType = '%s', componentId = '%s', pathMappingId = '%s')>" \
		% (self._path, self._server, self._location, self._branch, self._subBranch, self._controlProgram, self._point,\
		 self._zone, self._bacnetAddress, self._bacnetDevId, self._bacnetObjectType, self._pointType, self._componentId, self._pathMappingId)


class PathMapping(Base):
	"""Class to map to the DataPoints table in the HVAC DB"""

	__tablename__ = 'pathmappings'

	_id = Column('Id', Integer, primary_key = True)
	_path = Column('Path', String(255))
	_componentType = Column('ComponentType', String(255))
	_description = Column('Description', String(255))
	_databaseMapping = Column('DatabaseMapping', String(255))

	#PathMapping relationship
	_dataPoints = relationship("DataPoint", back_populates = "_pathMapping")

	#Constructor

	def __init__(self, identifier, path, componentType, description, databaseMapping, dataPoints = []):

		self._id = identifier
		self._path = path
		self._componentType = componentType
		self._description = description
		self._databaseMapping = databaseMapping
		self._dataPoints = dataPoints

	#Properties

	@property
	def id(self):
		return self._id

	@id.setter
	def id(self, value):
		self._id = value

	@property
	def path(self):
		return self._path

	@path.setter
	def path(self, value):
		self._path = value

	@property
	def componentType(self):
		return self._componentType

	@componentType.setter
	def componentType(self, value):
		self._componentType = value

	@property
	def description(self):
		return self._description

	@description.setter
	def description(self, value):
		self._description = value

	@property
	def databaseMapping(self):
		return self._databaseMapping

	@databaseMapping.setter
	def databaseMapping(self, value):
		self._databaseMapping = value

	@property
	def dataPoints(self):
		return self._dataPoints

	@dataPoints.setter
	def dataPoints(self, value):
		self._dataPoints = value

	def __str__(self):
		return "<DataPoint(id = '%s', path = '%s', componentType = '%s', description = '%s', databaseMapping = '%s')>" \
		% (self._id, self._path, self._componentType, self._description, self._databaseMapping)


class ComponentRelationship(Base):
	"""Class to map to the DataPoints table in the HVAC DB"""

	__tablename__ = 'componentrelationships'

	_componentName = Column('ComponentName', String(255), primary_key = True)
	_parentComponent = Column('ParentComponent', String(255), ForeignKey("componentrelationships.ComponentName"))
	_componentType = Column('ComponentType', String(255))
	_group = Column('ComponentGroup', String(255))

	#Relationships between Component parents and children
	#_parent = relationship("ComponentRelationship", back_populates = "_children")
	_children = relationship("ComponentRelationship", backref = backref('_parent', remote_side=[_componentName]))

	#Constructor

	def __init__(self, componentName, parentComponent, componentType, group, parent = None, children = []):

		self._componentName = componentName
		self._parentComponent = parentComponent
		self._componentType = componentType
		self._group = group
		self._parent = parent
		self._children = children

	#Properties

	@property
	def componentName(self):
		return self._componentName

	@componentName.setter
	def componentName(self, value):
		self._componentName = value

	@property
	def parentComponent(self):
		return self._parentComponent

	@parentComponent.setter
	def parentComponent(self, value):
		self._parentComponent = value

	@property
	def componentType(self):
		return self._componentType

	@componentType.setter
	def componentType(self, value):
		self._componentType = value

	@property
	def group(self):
		return self._group

	@group.setter
	def group(self, value):
		self._group = value

	@property
	def parent(self):
		return self._parent

	@parent.setter
	def parent(self, value):
		self._parent = value

	@property
	def children(self):
		return self._children

	@children.setter
	def children(self, value):
		self._children = value

	def __str__(self):
		return "<DataPoint(componentName = '%s', parentComponent = '%s', componentType = '%s', group = '%s')>" % (self._componentName, self._parentComponent, self._componentType, self._group)


class AHU(Base):
	"""Class to map to the Air_Handling_Unit table in the HVAC DB"""

	__tablename__ = "air_handling_unit"

	_AHUNumber = Column('AHUNumber', Integer, primary_key = True, autoincrement = True)
	_AHUName = Column('AHUName', String(255))

	#Relationships

	_ahuReadings = relationship('AHUReading', back_populates = '_ahu') #AHUReadings and AHU
	_filters = relationship('Filter', back_populates = '_ahu') #Filter and AHU
	_fans = relationship('Fan', back_populates = '_ahu') #Fan and AHU
	_dampers = relationship('Damper', back_populates = '_ahu') #Damper and AHU
	_vavs = relationship('VAV', back_populates = '_ahu') #VAV and AHU
	_savs = relationship('SAV', back_populates = '_ahu') #SAV and AHU
	_hecs = relationship('HEC', back_populates = '_ahu') #HEC and AHU
	_vfds = relationship('VFD', back_populates = '_ahu') #VFD and AHU
	_thermafusers = relationship('Thermafuser', back_populates = '_ahu') #Thermafuser and AHU

	#Constructor

	def __init__(self, AHUNumber, AHUName, ahuReadings = [], filters = [], fans = [], dampers = [], vavs = [], savs = [], hecs = [], vfds = [], thermafusers = []):

		self._AHUNumber = AHUNumber
		self._AHUName = AHUName
		self._ahuReadings = ahuReadings
		self._filters = filters
		self._fans = fans
		self._dampers = dampers
		self._vavs = vavs
		self._savs = savs
		self._hecs = hecs
		self._vfds = vfds
		self._thermafusers = thermafusers

	#Properties

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def AHUName(self):
		return self._AHUName

	@AHUName.setter
	def AHUName(self, value):
		self._AHUName = value

	@property
	def ahuReadings(self):
		return self._ahuReadings

	@ahuReadings.setter
	def ahuReadings(self, value):
		self._ahuReadings = value

	@property
	def filters(self):
		return self._filters

	@filters.setter
	def filters(self, value):
		self._filters = value

	@property
	def fans(self):
		return self._fans

	@fans.setter
	def fans(self, value):
		self._fans = value

	@property
	def dampers(self):
		return self._dampers

	@dampers.setter
	def dampers(self, value):
		self._dampers = value

	@property
	def vavs(self):
		return self._vavs

	@vavs.setter
	def vavs(self, value):
		self._vavs = value

	@property
	def savs(self):
		return self._savs

	@savs.setter
	def savs(self, value):
		self._savs = value

	@property
	def hecs(self):
		return self._hecs

	@hecs.setter
	def hecs(self, value):
		self._hecs = value

	@property
	def vfds(self):
		return self._vfds

	@vfds.setter
	def vfds(self, value):
		self._vfds = value

	@property
	def thermafusers(self):
		return self._thermafusers

	@thermafusers.setter
	def thermafusers(self, value):
		self._thermafusers = value

	#Methods

	def getComponentName(self):
		return self._AHUName

	def getComponentType(self):
		return "AHU"

	def __str__(self):
		return "<AHU(AHUNumber = '%d', AHUName = '%s')>" % (self._AHUNumber, self._AHUName)


class AHUReading(Base):
	"""Class to map to the Air Handling Unit Readings table in the HVAC DB"""

	__tablename__ = 'air_handling_unit_reading'

	_AHUNumber = Column('AHUNumber', Integer, ForeignKey("air_handling_unit.AHUNumber"), primary_key = True)
	_timestamp = Column('Time_stamp', DateTime, primary_key = True)
	_staticPressure = Column('StaticPressure', Float)
	_returnAirTemperature = Column('ReturnAirTemperature', Float, nullable=True)
	_supplyAirTemperature = Column('SupplyAirTemperature', Float, nullable=True)
	_outsideAirTemperature = Column('OutsideAirTemperature', Float, nullable=True)
	_outsideAirCo2 = Column('OutsideAirCO2', Float, nullable=True)
	_returnAirCo2 = Column('ReturnAirCO2', Float, nullable=True)
	_mixedAirTemperature = Column('MixedAirTemperature', Float, nullable=True)
	_OSACFM = Column('OutsideAirCFM', Float, nullable=True)
	_coolingRequest = Column('CoolingRequest', Float, nullable=True)
	_coolingSetpoint = Column('CoolingSetpoint', Float, nullable=True)
	_heatingRequest = Column('HeatingRequest', Float, nullable=True)
	_heatingSetpoint = Column('HeatingSetpoint', Float, nullable=True)
	_economizerSetpoint = Column('EconomizerSetpoint', Float, nullable=True)
	_occupiedMode = Column('OccupiedMode', Boolean, nullable=True)
	_returnAirCo2Setpoint = Column('ReturnAirCO2Setpoint', Float, nullable=True)
	_staticPressureSmoothed = Column('StaticPressureSmoothed', Float, nullable=True)
	_staticSP = Column('StaticSP', Float, nullable=True)
	_supplyAirSetpoint = Column('SupplyAirSetpoint', Float, nullable=True)
	_STReq = Column('STReq', Float, nullable=True)
	_staticSP1 = Column('StaticSP1', Float, nullable=True)
	_staticSP2 = Column('StaticSP2', Float, nullable=True)

	#Relationship between AHU Reading and AHU
	_ahu = relationship("AHU", back_populates = "_ahuReadings", cascade = "all, delete-orphan", single_parent = True)

	#Constructor

	def __init__(self, timestamp = None, AHUNumber = None, staticPressure = None, returnAirTemperature = None, supplyAirTemperature = None,\
	 outsideAirTemperature = None, outsideAirCo2 = None, returnAirCo2 = None,\
	  mixedAirTemperature = None, OSACFM = None, coolingRequest = None, coolingSetpoint = None, heatingRequest = None, heatingSetpoint = None, economizerSetpoint = None,\
	  occupiedMode = None, returnAirCo2Setpoint = None, staticPressureSmoothed = None, staticSP = None, supplyAirSetpoint = None, STReq = None, staticSP1 = None, staticSP2 = None, ahu = None):

		self._AHUNumber = AHUNumber
		self._timestamp = timestamp
		self._staticPressure = staticPressure
		self._returnAirTemperature = returnAirTemperature
		self._supplyAirTemperature = supplyAirTemperature
		self._outsideAirTemperature = outsideAirTemperature
		self._outsideAirCo2 = outsideAirCo2
		self._returnAirCo2 = returnAirCo2
		self._mixedAirTemperature = mixedAirTemperature
		self._OSACFM = OSACFM
		self._coolingRequest = coolingRequest
		self._coolingSetpoint = coolingSetpoint
		self._heatingRequest = heatingRequest
		self._heatingSetpoint = heatingSetpoint
		self._economizerSetpoint = economizerSetpoint
		self._occupiedMode = occupiedMode
		self._returnAirCo2Setpoint = returnAirCo2Setpoint
		self._staticPressureSmoothed = staticPressureSmoothed
		self._staticSP = staticSP
		self._supplyAirSetpoint = supplyAirSetpoint
		self._STReq = STReq
		self._staticSP1 = staticSP1
		self._staticSP2 = staticSP2
		self._ahu = ahu

	#properties

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		self._timestamp = value

	@property
	def staticPressure(self):
		return self._staticPressure

	@staticPressure.setter
	def staticPressure(self, value):
		self._staticPressure = float(value) if value != None else None

	@property
	def returnAirTemperature(self):
		return self._returnAirTemperature

	@returnAirTemperature.setter
	def returnAirTemperature(self, value):
		self._returnAirTemperature = float(value) if value != None else None

	@property
	def supplyAirTemperature(self):
		return self._supplyAirTemperature

	@supplyAirTemperature.setter
	def supplyAirTemperature(self, value):
		self._supplyAirTemperature = float(value) if value != None else None

	@property
	def outsideAirTemperature(self):
		return self._outsideAirTemperature

	@outsideAirTemperature.setter
	def outsideAirTemperature(self, value):
		self._outsideAirTemperature = float(value) if value != None else None

	@property
	def outsideAirCo2(self):
		return self._outsideAirCo2

	@outsideAirCo2.setter
	def outsideAirCo2(self, value):
		self._outsideAirCo2 = float(value) if value != None else None

	@property
	def returnAirCo2(self):
		return self._returnAirCo2

	@returnAirCo2.setter
	def returnAirCo2(self, value):
		self._returnAirCo2 = float(value) if value != None else None

	@property
	def mixedAirTemperature(self):
		return self._mixedAirTemperature

	@mixedAirTemperature.setter
	def mixedAirTemperature(self, value):
		self._mixedAirTemperature = float(value) if value != None else None

	@property
	def OSACFM(self):
		return self._OSACFM

	@OSACFM.setter
	def OSACFM(self, value):
		self._OSACFM = float(value) if value != None else None

	@property
	def coolingRequest(self):
		return self._coolingRequest

	@coolingRequest.setter
	def coolingRequest(self, value):
		self._coolingRequest = float(value) if value != None else None

	@property
	def coolingSetpoint(self):
		return self._coolingSetpoint

	@coolingSetpoint.setter
	def coolingSetpoint(self, value):
		self._coolingSetpoint = float(value) if value != None else None

	@property
	def heatingRequest(self):
		return self._heatingRequest

	@heatingRequest.setter
	def heatingRequest(self, value):
		self._heatingRequest = float(value) if value != None else None

	@property
	def heatingSetpoint(self):
		return self._heatingSetpoint

	@heatingSetpoint.setter
	def heatingSetpoint(self, value):
		self._heatingSetpoint = float(value) if value != None else None

	@property
	def economizerSetpoint(self):
		return self._economizerSetpoint

	@economizerSetpoint.setter
	def economizerSetpoint(self, value):
		self._economizerSetpoint = float(value) if value != None else None

	@property
	def occupiedMode(self):
		return self._occupiedMode

	@occupiedMode.setter
	def occupiedMode(self, value):
		self._occupiedMode = bool(value) if value != None else None

	@property
	def returnAirCo2Setpoint(self):
		return self._returnAirCo2Setpoint

	@returnAirCo2Setpoint.setter
	def returnAirCo2Setpoint(self, value):
		self._returnAirCo2Setpoint = float(value) if value != None else None

	@property
	def staticPressureSmoothed(self):
		return self._staticPressureSmoothed

	@staticPressureSmoothed.setter
	def staticPressureSmoothed(self, value):
		self._staticPressureSmoothed = float(value) if value != None else None

	@property
	def staticSP(self):
		return self._staticSP

	@staticSP.setter
	def staticSP(self, value):
		self._staticSP = float(value) if value != None else None

	@property
	def supplyAirSetpoint(self):
		return self._supplyAirSetpoint

	@supplyAirSetpoint.setter
	def supplyAirSetpoint(self, value):
		self._supplyAirSetpoint = float(value) if value != None else None

	@property
	def STReq(self):
		return self._STReq

	@STReq.setter
	def STReq(self, value):
		self._STReq = float(value) if value != None else None

	@property
	def staticSP1(self):
		return self._staticSP1

	@staticSP1.setter
	def staticSP1(self, value):
		self._staticSP1 = float(value) if value != None else None

	@property
	def staticSP2(self):
		return self._staticSP2

	@staticSP2.setter
	def staticSP2(self, value):
		self._staticSP2 = float(value) if value != None else None

	@property
	def ahu(self):
		return self._ahu

	@ahu.setter
	def ahu(self, value):
		self._ahu = value

	def to_json(self):

		json_text = {'timestamp': str(datetime.now()), 'staticPressure': self._staticPressure, 'supplyAirTemperature': self._supplyAirTemperature,
			   'outsideAirTemperature': self._outsideAirTemperature, 'outsideAirCo2': self._outsideAirCo2, 'returnAirCo2': self._returnAirCo2,
			   'mixedAirTemperature': self._mixedAirTemperature, 'OSACFM': self._OSACFM, 'coolingRequest': self._coolingRequest,
				'coolingSetpoint': self._coolingSetpoint, 'heatingRequest': self._heatingRequest, 'heatingSetpoint': self._heatingSetpoint,
				'economizerSetpoint': self._economizerSetpoint, 'occupiedMode': self._occupiedMode, 'returnAirCo2Setpoint': self._returnAirCo2Setpoint,
				'staticPressureSmoothed': self._staticPressureSmoothed, 'staticSP': self._staticSP, 'supplyAirSetpoint': self._supplyAirSetpoint,
				'STReq': self._STReq, 'staticSP1': self._staticSP1, 'staticSP2': self._staticSP2}

		return json_text

	def __str__(self):
		return "<AHUReading(AHUNumber = '%s', timestamp = '%s', staticPressure = '%s', returnAirTemperature = '%s', supplyAirTemperature = '%s', \
		outsideAirTemperature = '%s' outsideAirCo2 = '%s', returnAirCo2 = '%s', \
		mixedAirTemperature = '%s', OSACFM = '%s', CoolingRequest = '%s', CoolingSetpoint = '%s', HeatingRequest = '%s', HeatingSetpoint = '%s',\
		EconomizerSetpoint = '%s', OccupiedMode = '%s', ReturnAirCo2Setpoint = '%s', StaticPressureSmoothed = '%s', StaticSP = '%s', supplyAirSetpoint = '%s', STReq = '%s',\
		StaticSP1 = '%s', StaticSP2 = '%s')>" \
		% (self._AHUNumber, str(self._timestamp), self._staticPressure, self._returnAirTemperature, self._supplyAirTemperature, \
		 self._outsideAirTemperature, self._outsideAirCo2, self._returnAirCo2, \
		 self._mixedAirTemperature, self._OSACFM, self._coolingRequest, self._coolingSetpoint, self._heatingRequest, self._heatingSetpoint,\
		 self._economizerSetpoint, self._occupiedMode, self._returnAirCo2Setpoint, self._staticPressureSmoothed, self._staticSP, self._supplyAirSetpoint, self._STReq,\
		 self._staticSP1, self._staticSP2)



class VFD(Base):
	"""Class to map to the Filter table in the HVAC DB"""

	__tablename__ = "vfd"

	_vfdId = Column('VFDId', Integer, primary_key = True, autoincrement = True)
	_AHUNumber = Column('AHUNumber', Integer, ForeignKey("air_handling_unit.AHUNumber"))
	_vfdName = Column('VFDName', String(255))
	_vfdType = Column('VFDType', String(255))

	#Relationships
	_ahu = relationship("AHU", back_populates = "_vfds") #Relatiionship between Filter and AHU
	_vfdReadings = relationship("VFDReading", back_populates = "_vfd") #Relationship between Filter and Filter_Reading

	#Constructor

	def __init__(self, vfdId, AHUNumber, vfdName, vfdType, ahu = None, vfdReadings = []):

		self._vfdId = vfdId
		self._vfdName = vfdName
		self._AHUNumber = AHUNumber
		self._vfdType = vfdType
		self._ahu = ahu
		self._vfdReadings = vfdReadings

	#Properties

	@property
	def vfdId(self):
		return self._vfdId

	@vfdId.setter
	def vfdId(self, value):
		self._vfdId = value

	@property
	def vfdName(self):
		return self._vfdName

	@vfdName.setter
	def vfdName(self, value):
		self._vfdName = value

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def vfdType(self):
		return self._vfdType

	@vfdType.setter
	def vfdType(self, value):
		self._vfdType = value

	@property
	def ahu(self):
		return self._ahu

	@ahu.setter
	def ahu(self, value):
		self._ahu = value

	@property
	def vfdReadings(self):
		return self._vfdReadings

	@vfdReadings.setter
	def vfdReadings(self, value):
		self._vfdReadings = value

	#Methods

	def getComponentName(self):
		return self._vfdName

	def getComponentType(self):
		return "VFD" + self._vfdType

	def __str__(self):
		return "<Filter(vfdId = '%d', AHUNumber = '%d', vfdName = '%s',  vfdType = '%s')>" % (self._vfdId, self._AHUNumber, self._vfdName, self._vfdType)


class VFDReading(Base):
	"""Class to map to the Filter_Reading table in the HVAC DB"""

	__tablename__ = "vfd_reading"

	_timestamp = Column('Time_stamp', DateTime, primary_key = True)
	_vfdId = Column('VFDId', Integer, ForeignKey("vfd.VFDId"), primary_key = True)
	_powerKW = Column('PowerKW', Float, nullable=True)
	_speedRPM = Column('SpeedRPM', Float, nullable=True)

	#Relationship between Filter and Filter_Reading
	_vfd = relationship("VFD", back_populates = "_vfdReadings", cascade = "all, delete-orphan", single_parent = True)

	#Constructor

	def __init__(self, timestamp = None, vfdId = None, powerKW = None, speedRPM = None, vfdRef = None):

		self._timestamp = timestamp
		self._vfdId = vfdId
		self._powerKW = powerKW
		self._speedRPM = speedRPM
		self._vfd = vfdRef

	#Properties

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		self._timestamp = value

	@property
	def vfdId(self):
		return self._vfdId

	@vfdId.setter
	def vfdId(self, value):
		self._vfdId = value

	@property
	def powerKW(self):
		return self._powerKW

	@powerKW.setter
	def powerKW(self, value):
		self._powerKW = float(value) if value != None else None

	@property
	def speedRPM(self):
		return self._speedRPM

	@speedRPM.setter
	def speedRPM(self, value):
		self._speedRPM = float(value) if value != None else None

	@property
	def vfd(self):
		return self._vfd

	@vfd.setter
	def vfd(self, value):
		self._vfd = value

	def to_json(self):

		json_text = {'timestamp': str(datetime.now()), 'powerKW': self._powerKW, 'speedRPM': self._speedRPM}

		return json_text

	def __str__(self):
		return "<FilterReading(timestamp = '%s', vfdId = '%s', powerKW = '%s', speedRPM = '%s')>" % (str(self._timestamp), self._vfdId, self._powerKW, self._speedRPM)


class Filter(Base):
	"""Class to map to the Filter table in the HVAC DB"""

	__tablename__ = "filter"

	_filterId = Column('FilterId', Integer, primary_key = True, autoincrement = True)
	_AHUNumber = Column('AHUNumber', Integer, ForeignKey("air_handling_unit.AHUNumber"))
	_filterName = Column('FilterName', String(255))
	_filterType = Column('FilterType', String(255))

	#Relationships
	_ahu = relationship("AHU", back_populates = "_filters") #Relatiionship between Filter and AHU
	_filterReadings = relationship("FilterReading", back_populates = "_filter") #Relationship between Filter and Filter_Reading

	#Constructor

	def __init__(self, filterId, AHUNumber, filterName, filterType = None, ahu = None, filterReadings = []):

		self._filterId = filterId
		self._filterName = filterName
		self._AHUNumber = AHUNumber
		self._filterType = filterType
		self._ahu = ahu
		self._filterReadings = filterReadings

	#Properties

	@property
	def filterId(self):
		return self._filterId

	@filterId.setter
	def filterId(self, value):
		self._filterId = value

	@property
	def filterName(self):
		return self._filterName

	@filterName.setter
	def filterName(self, value):
		self._filterName = value

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def filterType(self):
		return self._filterType

	@filterType.setter
	def filterType(self, value):
		self._filterType = value

	@property
	def ahu(self):
		return self._ahu

	@ahu.setter
	def ahu(self, value):
		self._ahu = value

	@property
	def filterReadings(self):
		return self._filterReadings

	@filterReadings.setter
	def filterReadings(self, value):
		self._filterReadings = value

	#Methods

	def getComponentName(self):
		return self._filterName

	def getComponentType(self):
		return "Filter" + self._filterType

	def __str__(self):
		return "<Filter(filterId = '%d', AHUNumber = '%d', filterName = '%s', filterType = '%s')>" % (self._filterId, self._AHUNumber, self._filterName, self._filterType)


class FilterReading(Base):
	"""Class to map to the Filter_Reading table in the HVAC DB"""

	__tablename__ = "filter_reading"

	_timestamp = Column('Time_stamp', DateTime, primary_key = True)
	_filterId = Column('FilterId', Integer, ForeignKey("filter.FilterId"), primary_key = True)
	_differencePressure = Column('DifferencePressure', Float, nullable=True)

	#Relationship between Filter and Filter_Reading
	_filter = relationship("Filter", back_populates = "_filterReadings", cascade = "all, delete-orphan", single_parent = True)

	#Constructor

	def __init__(self, timestamp = None, filterId = None, differencePressure = None, filterRef = None):

		self._timestamp = timestamp
		self._filterId = filterId
		self._differencePressure = differencePressure
		self._filter = filterRef

	#Properties

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		self._timestamp = value

	@property
	def filterId(self):
		return self._filterId

	@filterId.setter
	def filterId(self, value):
		self._filterId = value

	@property
	def differencePressure(self):
		return self._differencePressure

	@differencePressure.setter
	def differencePressure(self, value):
		self._differencePressure = float(value) if value != None else None

	@property
	def filter(self):
		return self._filter

	@filter.setter
	def filter(self, value):
		self._filter = value

	def to_json(self):

		json_text = {'timestamp': str(datetime.now()), 'differencePressure': self._differencePressure}

		return json_text

	def __str__(self):
		return "<FilterReading(timestamp = '%s', filterId = '%s', differencePressure = '%s')>" % (str(self._timestamp), self._filterId, self._differencePressure)


class Damper(Base):
	"""Class to map to the Damper table in the HVAC DB"""

	__tablename__ = "damper"

	_damperId = Column('DamperId', Integer, primary_key = True, autoincrement = True)
	_AHUNumber = Column('AHUNumber', Integer, ForeignKey("air_handling_unit.AHUNumber"))
	_damperName = Column('DamperName', String(255))
	_damperType = Column('DamperType', String(255))

	#Relationships

	_ahu = relationship("AHU", back_populates = "_dampers") #Relatiionship between Damper and AHU
	_damperReadings = relationship("DamperReading", back_populates = "_damper") #Relationship between Damper and Damper_Reading

	#Constructor

	def __init__(self, damperId, AHUNumber, damperName, damperType = None, ahu = None, damperReadings = []):

		self._damperId = damperId
		self._AHUNumber = AHUNumber
		self._damperName = damperName
		self._damperType = damperType
		self._ahu = ahu
		self._damperReadings = damperReadings

	#Properties

	@property
	def damperId(self):
		return self._damperId

	@damperId.setter
	def damperId(self, value):
		self._damperId = value

	@property
	def damperName(self):
		return self._damperName

	@damperName.setter
	def damperName(self, value):
		self._damperName = value

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def damperType(self):
		return self._damperType

	@damperType.setter
	def damperType(self, value):
		self._damperType = value

	@property
	def ahu(self):
		return self._ahu

	@ahu.setter
	def ahu(self, value):
		self._ahu = value

	@property
	def damperReadings(self):
		return self._damperReadings

	@damperReadings.setter
	def damperReadings(self, value):
		self._damperReadings = value

	#Methods

	def getComponentName(self):
		return self._damperName

	def getComponentType(self):
		return "Damper" + self._damperType

	def __str__(self):
		return "<Damper(damperId = '%d', AHUNumber = '%d', damperName = '%s', damperType = '%s')>" % (self._damperId, self._AHUNumber, self._damperName, self._damperType)


class DamperReading(Base):
	"""Class to map to the Damper_Reading table in the HVAC DB"""

	__tablename__ = 'damper_reading'

	_damperId = Column('DamperId', Integer, ForeignKey("damper.DamperId"), primary_key = True)
	_timestamp = Column('Time_stamp', DateTime, primary_key=True)
	_damperOpeningPercentage = Column('DamperOpeningPercentage', Float, nullable=True)

	#Relationship between Damper and Damper_Reading
	_damper = relationship("Damper", back_populates = "_damperReadings", cascade = "all, delete-orphan", single_parent = True)

	#Constructor

	def __init__(self, timestamp = None, damperId = None, damperOpeningPercentage = None, damper = None):

		self._damperId = damperId
		self._timestamp = timestamp
		self._damperOpeningPercentage = damperOpeningPercentage
		self._damper = damper

	#properties

	@property
	def damperId(self):
		return self._damperId

	@damperId.setter
	def damperId(self, value):
		self._damperId = value

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		self._timestamp = value

	@property
	def damperOpeningPercentage(self):
		return self._damperOpeningPercentage

	@damperOpeningPercentage.setter
	def damperOpeningPercentage(self, value):
		self._damperOpeningPercentage = float(value) if value != None else None

	@property
	def damper(self):
		return self._damper

	@damper.setter
	def damper(self, value):
		self._damper = value

	def to_json(self):

		json_text = {'timestamp': str(datetime.now()), 'damperOpeningPercentage': self._damperOpeningPercentage}

		return json_text

	def __str__(self):
		return "<DamperReading(damperId = '%s', timestamp = '%s', damperOpeningPercentage = '%s')>" \
		% (self._damperId, str(self._timestamp), self._damperOpeningPercentage)


class Fan(Base):
	"""Class to map to the Fan table in the HVAC DB"""

	__tablename__ = "fan"

	_fanId = Column('FanId', Integer, primary_key = True, autoincrement = True)
	_AHUNumber = Column('AHUNumber', Integer, ForeignKey("air_handling_unit.AHUNumber"))
	_fanName = Column('FanName', String(255))
	_fanType = Column('FanType', String(255))

	#Relationships

	_ahu = relationship("AHU", back_populates = "_fans") #Relationship between Fan and AHU
	_fanReadings = relationship("FanReading", back_populates = "_fan") #Relationship between Fan and Fan_Reading

	#Constructor

	def __init__(self, fanId, AHUNumber, fanName, fanType = None, ahu = None, fanReadings = []):

		self._fanId = fanId
		self._AHUNumber = AHUNumber
		self._fanName = fanName
		self._fanType = fanType
		self._ahu = ahu
		self._fanReadings = fanReadings

	#Properties

	@property
	def fanId(self):
		return self._fanId

	@fanId.setter
	def fanId(self, value):
		self._fanId = value

	@property
	def fanName(self):
		return self._fanName

	@fanName.setter
	def fanName(self, value):
		self._fanName = value

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def fanType(self):
		return self._fanType

	@fanType.setter
	def fanType(self, value):
		self._fanType = value

	@property
	def ahu(self):
		return self._ahu

	@ahu.setter
	def ahu(self, value):
		self._ahu = value

	@property
	def fanReadings(self):
		return self._fanReadings

	@fanReadings.setter
	def fanReadings(self, value):
		self._fanReadings = value

	#Methods

	def getComponentName(self):
		return self._fanName

	def getComponentType(self):
		return "Fan" + self._fanType

	def __str__(self):
		return "<Fan(fanId = '%d', AHUNumber = '%d', fanName = '%s', fanType = '%s')>" % (self._fanId, self._AHUNumber, self._fanName, self._fanType)


class FanReading(Base):
	"""Class to map to the Fan Reading table in the HVAC DB"""

	__tablename__ = 'fan_reading'

	_fanId = Column('FanId', Integer, ForeignKey("fan.FanId"), primary_key = True)
	_timestamp = Column('Time_stamp', DateTime, primary_key = True)
	_airVelocityPressure = Column('AirVelocityPressure', Float, nullable=True)
	_airVelocityCFM = Column('AirVelocityCFM', Float, nullable=True)

	#Relationship between Fan and Fan_Reading
	_fan = relationship("Fan", back_populates = "_fanReadings", cascade = "all, delete-orphan", single_parent = True)

	#Constructor

	def __init__(self, timestamp = None, fanId = None, airVelocityPressure = None, airVelocityCFM = None, fan = None):

		self._fanId = fanId
		self._timestamp = timestamp
		self._airVelocityPressure = airVelocityPressure
		self._airVelocityCFM = airVelocityCFM
		self._fan = fan

	#properties

	@property
	def fanId(self):
		return self._fanId

	@fanId.setter
	def fanId(self, value):
		self._fanId = value

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		self._timestamp = value

	@property
	def airVelocityPressure(self):
		return self._airVelocityPressure

	@airVelocityPressure.setter
	def airVelocityPressure(self, value):
		self._airVelocityPressure = float(value) if value != None else None

	@property
	def airVelocityCFM(self):
		return self._airVelocityCFM

	@airVelocityCFM.setter
	def airVelocityCFM(self, value):
		self._airVelocityCFM = float(value) if value != None else None

	@property
	def fan(self):
		return self._fan

	@fan.setter
	def fan(self, value):
		self._fan = value

	def to_json(self):

		json_text = {'timestamp': str(datetime.now()), 'airVelocityPressure': self._airVelocityPressure, 'airVelocityCFM': self._airVelocityCFM}

		return json_text

	def __str__(self):
		return "<FanReading(fanId = '%s', timestamp = '%s', 'airVelocityPressure' = '%s', airVelocityCFM = '%s')>" \
		% (self._fanId, str(self._timestamp), self.airVelocityPressure, self._airVelocityCFM)


class HEC(Base):
	"""Class to map to the HEC table in the HVAC DB"""

	__tablename__ = "heat_exchanger_coil"

	_HECId = Column('HECId', Integer, primary_key = True, autoincrement = True)
	_AHUNumber = Column('AHUNumber', Integer, ForeignKey("air_handling_unit.AHUNumber"), nullable = True)
	_SAVId = Column('SAVId', Integer, ForeignKey("staged_air_volume.SAVId"), nullable = True)
	_VAVId = Column('VAVId', Integer, ForeignKey("variable_air_volume.VAVId"), nullable = True)
	_HECName = Column('HECName', String(255))
	_HECType = Column('HECType', String(255))

	#Relationships

	_ahu = relationship("AHU", back_populates = "_hecs") #Relationship between HEC and AHU
	_vav = relationship("VAV", back_populates = "_hecs") #Relationship between HEC and VAV
	_sav = relationship("SAV", back_populates = "_hecs") #Relationship between HEC and SAV
	_hecReadings = relationship("HECReading", back_populates = "_hec") #Relationship between HEC and HEC_Reading

	#Constructor

	def __init__(self, HECId, HECName, HECType = None, AHUNumber = None, VAVId = None, SAVId = None, ahu = None, vav = None, sav = None, hecReadings = []):

		self._HECId = HECId
		self._HECName = HECName
		self._HECType = HECType
		self._AHUNumber = AHUNumber
		self._VAVId = VAVId
		self._SAVId = SAVId
		self._ahu = ahu
		self._vav = vav
		self._sav = sav
		self._hecReadings = hecReadings

	#Properties

	@property
	def HECId(self):
		return self._HECId

	@HECId.setter
	def HECId(self, value):
		self._HECId = value

	@property
	def HECName(self):
		return self._HECName

	@HECName.setter
	def HECName(self, value):
		self._HECName = value

	@property
	def HECType(self):
		return self._HECType

	@HECType.setter
	def HECType(self, value):
		self._HECType = value

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def VAVId(self):
		return self._VAVId

	@VAVId.setter
	def VAVId(self, value):
		self._VAVId = value

	@property
	def SAVId(self):
		return self._SAVId

	@SAVId.setter
	def SAVId(self, value):
		self._SAVId = value

	@property
	def vav(self):
		return self._vav

	@vav.setter
	def vav(self, value):
		self._vav = value

	@property
	def sav(self):
		return self._sav

	@sav.setter
	def sav(self, value):
		self._sav = value

	@property
	def ahu(self):
		return self._ahu

	@ahu.setter
	def ahu(self, value):
		self._ahu = value

	@property
	def hecReadings(self):
		return self._hecReadings

	@hecReadings.setter
	def hecReadings(self, value):
		self._hecReadings = value

	#Methods

	def getComponentName(self):
		return self._HECName

	def getComponentType(self):
		return "HEC" + self._HECType

	def __str__(self):
		return "<HEC(HECId = '%d', AHUNumber = '%s', HECName = '%s', HECType = '%s', SAVId = '%s', VAVId = '%s')>" \
		% (self._HECId, str(self._AHUNumber), self._HECName, self._HECType, str(self._SAVId), str(self._VAVId))


class HECReading(Base):
	"""Class to map to the Heat Exchanger Coil Readings table in the HVAC DB"""

	__tablename__ = 'heat_exchanger_coil_reading'

	_HECId = Column('HECId', Integer, ForeignKey("heat_exchanger_coil.HECId"), primary_key = True)
	_timestamp = Column('Time_stamp', DateTime, primary_key = True)
	_supplyWaterTemperature = Column('SupplyWaterTemperature', Float, nullable=True)
	_returnWaterTemperature = Column('ReturnWaterTemperature', Float, nullable=True)
	_valveOpeningPercentage = Column('valveOpeningPercentage', Float, nullable=True)

	#Relationship between HEC Reading and HEC
	_hec = relationship("HEC", back_populates = "_hecReadings", cascade = "all, delete-orphan", single_parent = True)

	#Constructor

	def __init__(self, timestamp = None, HECId = None, supplyWaterTemperature = None, returnWaterTemperature = None, valveOpeningPercentage = None, hec = None):

		self._HECId = HECId
		self._timestamp = timestamp
		self._supplyWaterTemperature = supplyWaterTemperature
		self._returnWaterTemperature = returnWaterTemperature
		self._valveOpeningPercentage = valveOpeningPercentage
		self._hec = hec

	#properties

	@property
	def HECId(self):
		return self._HECId

	@HECId.setter
	def HECId(self, value):
		self._HECId = value

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		self._timestamp = value

	@property
	def supplyWaterTemperature(self):
		return self._supplyWaterTemperature

	@supplyWaterTemperature.setter
	def supplyWaterTemperature(self, value):
		self._supplyWaterTemperature = float(value) if value != None else None

	@property
	def returnWaterTemperature(self):
		return self._returnWaterTemperature

	@returnWaterTemperature.setter
	def returnWaterTemperature(self, value):
		self._returnWaterTemperature = float(value) if value != None else None

	@property
	def valveOpeningPercentage(self):
		return self._valveOpeningPercentage

	@valveOpeningPercentage.setter
	def valveOpeningPercentage(self, value):
		self._valveOpeningPercentage = float(value) if value != None else None

	@property
	def hec(self):
		return self._hec

	@hec.setter
	def hec(self, value):
		self._hec = value

	def to_json(self):

		json_text = {'timestamp': str(datetime.now()), 'supplyWaterTemperature': self._supplyWaterTemperature, 'returnWaterTemperature': self._returnWaterTemperature,
					 'valveOpeningPercentage': self._valveOpeningPercentage}

		return json_text

	def __str__(self):
		return "<HECReading(HECId = '%s', timestamp = '%s', supplyWaterTemperature = '%s', returnWaterTemperature = '%s', valveOpeningPercentage = '%s')>" \
		% (self._HECId, str(self._timestamp), self._supplyWaterTemperature, self._returnWaterTemperature, self._valveOpeningPercentage)


class SAV(Base):
	"""Class to map to the SAV table in the HVAC DB"""

	__tablename__ = "staged_air_volume"

	_SAVId = Column('SAVId', Integer, primary_key = True, autoincrement = True)
	_AHUNumber = Column('AHUNumber', Integer, ForeignKey("air_handling_unit.AHUNumber"), nullable = True)
	_SAVName = Column('SAVName', String(255))

	#Relationships
	_ahu = relationship("AHU", back_populates = "_savs") #Relationship between SAV and AHU
	_hecs = relationship("HEC", back_populates = "_sav") #Relationship between SAV and HEC
	_thermafusers = relationship("Thermafuser", back_populates = "_sav") #Relationship between SAV and Thermafuser
	_savReadings = relationship("SAVReading", back_populates = "_sav") #Relationship between SAV and SAV_Reading

	#Constructor

	def __init__(self, SAVId, AHUNumber, SAVName, ahu = None, hecs = [], thermafusers = [], SAVReadings = []):

		self._SAVId = SAVId
		self._AHUNumber = AHUNumber
		self._SAVName = SAVName
		self._ahu = ahu
		self._hecs = hecs
		self._SAVReadings = SAVReadings
		self._thermafusers = thermafusers

	#Properties

	@property
	def SAVId(self):
		return self._SAVId

	@SAVId.setter
	def SAVId(self, value):
		self._SAVId = value

	@property
	def SAVName(self):
		return self._SAVName

	@SAVName.setter
	def SAVName(self, value):
		self._SAVName = value

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def ahu(self):
		return self._ahu

	@ahu.setter
	def ahu(self, value):
		self._ahu = value

	@property
	def hecs(self):
		return self._hecs

	@hecs.setter
	def hecs(self, value):
		self._hecs = value

	@property
	def thermafusers(self):
		return self._thermafusers

	@thermafusers.setter
	def thermafusers(self, value):
		self._thermafusers = value

	@property
	def SAVReadings(self):
		return self._SAVReadings

	@SAVReadings.setter
	def SAVReadings(self, value):
		self._SAVReadings = value

	#Methods

	def getComponentName(self):
		return self._SAVName

	def getComponentType(self):
		return "SAV"

	def __str__(self):
		return "<SAV(SAVId = '%d', AHUNumber = '%d', SAVName = '%s')>" % (self._SAVId, self._SAVName)


class SAVReading(Base):
	"""Class to map to the SAV Readings table in the HVAC DB"""

	__tablename__ = 'staged_air_volume_reading'

	_SAVId = Column('SAVId', Integer, ForeignKey("staged_air_volume.SAVId"), primary_key = True)
	_timestamp = Column('Time_stamp', DateTime, primary_key = True)
	_zoneTemperature = Column('ZoneTemperature', Float, nullable=True)
	_dischargeTemperature = Column('DischargeTemperature', Float, nullable=True)
	_GEXDamperPosition = Column('GEXDamperPosition', Float, nullable=True)
	_coolingRequest = Column('CoolingRequest', Boolean, nullable=True)
	_heatingRequest = Column('HeatingRequest', Boolean, nullable=True)
	_damperPosition = Column('DamperPosition', Float, nullable=True)
	_exhaustAirflow = Column('ExhaustAirflow', Float, nullable=True)
	_supplyAirflow = Column('SupplyAirflow', Float, nullable=True)
	_flowDifference = Column('FlowDifference', Float, nullable=True)
	_exhaustFlowSetpoint = Column('ExhaustFlowSetpoint', Float, nullable=True)
	_heatingPercentage = Column('HeatingPercentage', Float, nullable=True)
	_coolingPercentage = Column('CoolingPercentage', Float, nullable=True)
	_coolingSetpoint = Column('CoolingSetpoint', Float, nullable=True)
	_heatingSetpoint = Column('HeatingSetpoint', Float, nullable=True)


	#Relationship between SAV Reading and SAV
	_sav = relationship("SAV", back_populates = "_savReadings", cascade = "all, delete-orphan", single_parent = True)

	#Constructor

	def __init__(self, timestamp = None, SAVId = None, zoneTemperature = None, dischargeTemperature = None, \
		GEXDamperPosition = None, coolingRequest = None, heatingRequest = None, damperPosition = None,\
	 	exhaustAirflow = None, supplyAirflow = None, flowDifference = None, exhaustFlowSetpoint = None, heatingPercentage = None, coolingPercentage = None,\
	 	coolingSetpoint = None, heatingSetpoint = None, sav = None):

		self._SAVId = SAVId
		self._timestamp = timestamp
		self._zoneTemperature = zoneTemperature
		self._dischargeTemperature = dischargeTemperature
		self._GEXDamperPosition = GEXDamperPosition
		self._coolingRequest = coolingRequest
		self._heatingRequest = heatingRequest
		self._damperPosition = damperPosition
		self._exhaustAirflow = exhaustAirflow
		self._supplyAirflow = supplyAirflow
		self._flowDifference = flowDifference
		self._exhaustFlowSetpoint = exhaustFlowSetpoint
		self._heatingPercentage = heatingPercentage
		self._coolingPercentage = coolingPercentage
		self._coolingSetpoint = coolingSetpoint
		self._heatingSetpoint = heatingSetpoint
		self._sav = sav

	#properties

	@property
	def SAVId(self):
		return self._SAVId

	@SAVId.setter
	def SAVId(self, value):
		self._SAVId = value

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		self._timestamp = value

	@property
	def zoneTemperature(self):
		return self._zoneTemperature

	@zoneTemperature.setter
	def zoneTemperature(self, value):
		self._zoneTemperature = float(value) if value != None else None

	@property
	def dischargeTemperature(self):
		return self._dischargeTemperature

	@dischargeTemperature.setter
	def dischargeTemperature(self, value):
		self._dischargeTemperature = float(value) if value != None else None

	@property
	def GEXDamperPosition(self):
		return self._GEXDamperPosition

	@GEXDamperPosition.setter
	def GEXDamperPosition(self, value):
		self._GEXDamperPosition = float(value) if value != None else None

	@property
	def coolingRequest(self):
		return self._coolingRequest

	@coolingRequest.setter
	def coolingRequest(self, value):
		self._coolingRequest = bool(value) if value != None else None

	@property
	def heatingRequest(self):
		return self._heatingRequest

	@heatingRequest.setter
	def heatingRequest(self, value):
		self._heatingRequest = bool(value) if value != None else None

	@property
	def damperPosition(self):
		return self._damperPosition

	@damperPosition.setter
	def damperPosition(self, value):
		self._damperPosition = float(value) if value != None else None

	@property
	def exhaustAirflow(self):
		return self._exhaustAirflow

	@exhaustAirflow.setter
	def exhaustAirflow(self, value):
		self._exhaustAirflow = float(value) if value != None else None

	@property
	def supplyAirflow(self):
		return self._supplyAirflow

	@supplyAirflow.setter
	def supplyAirflow(self, value):
		self._supplyAirflow = float(value) if value != None else None

	@property
	def flowDifference(self):
		return self._flowDifference

	@flowDifference.setter
	def flowDifference(self, value):
		self._flowDifference = float(value) if value != None else None

	@property
	def exhaustFlowSetpoint(self):
		return self._exhaustFlowSetpoint

	@exhaustFlowSetpoint.setter
	def exhaustFlowSetpoint(self, value):
		self._exhaustFlowSetpoint = float(value) if value != None else None

	@property
	def heatingPercentage(self):
		return self._heatingPercentage

	@heatingPercentage.setter
	def heatingPercentage(self, value):
		self._heatingPercentage = float(value) if value != None else None

	@property
	def coolingPercentage(self):
		return self._coolingPercentage

	@coolingPercentage.setter
	def coolingPercentage(self, value):
		self._coolingPercentage = float(value) if value != None else None

	@property
	def coolingSetpoint(self):
		return self._coolingSetpoint

	@coolingSetpoint.setter
	def coolingSetpoint(self, value):
		self._coolingSetpoint = float(value) if value != None else None

	@property
	def heatingSetpoint(self):
		return self._heatingSetpoint

	@heatingSetpoint.setter
	def heatingSetpoint(self, value):
		self._heatingSetpoint = float(value) if value != None else None

	@property
	def sav(self):
		return self._sav

	@sav.setter
	def sav(self, value):
		self._sav = value

	def to_json(self):

		json_text = {'timestamp': str(datetime.now()), 'zoneTemperature': self._zoneTemperature, 'dischargeTemperature': self._dischargeTemperature,
					 'GEXDamperPosition': self._GEXDamperPosition, 'coolingRequest': self._coolingRequest, 'heatingRequest': self._heatingRequest,
					 'damperPosition': self._damperPosition, 'exhaustAirflow': self._exhaustAirflow, 'supplyAirflow': self._supplyAirflow,
					 'flowDifference': self._flowDifference, 'exhaustFlowSetpoint': self._exhaustFlowSetpoint, 'heatingPercentage': self._heatingPercentage,
					 'coolingPercentage': self._coolingPercentage, 'coolingSetpoint': self._coolingSetpoint, 'heatingSetpoint': self._heatingSetpoint,}

		return json_text

	def __str__(self):
		return "<SAVReading(SAVId = '%s', timestamp = '%s', zoneTemperature = '%s', dischargeTemperature = '%s',\
		 GEXDamperPosition = '%s', coolingRequest = '%s', heatingRequest = '%s', damperPosition = '%s', exhaustAirflow = '%s', supplyAirflow = '%s', flowDifference = '%s'\
		 exhaustFlowSetpoint = '%s', heatingPercentage = '%s', coolingPercentage = '%s', coolingSetpoint = '%s', heatingSetpoint = '%s')>" \
		% (self._SAVId, str(self._timestamp), self._zoneTemperature, self._dischargeTemperature, \
		 self._GEXDamperPosition, self._coolingRequest, self._heatingRequest,\
		 self._damperPosition, self._exhaustAirflow, self._supplyAirflow, self._flowDifference, self._exhaustFlowSetpoint,\
		 self._heatingPercentage, self._coolingPercentage, self._coolingSetpoint, self._heatingSetpoint)


class VAV(Base):
	"""Class to map to the Filter table in the HVAC DB"""

	__tablename__ = "variable_air_volume"

	_VAVId = Column('VAVId', Integer, primary_key = True, autoincrement = True)
	_AHUNumber = Column('AHUNumber', Integer, ForeignKey("air_handling_unit.AHUNumber"))
	_VAVName = Column('VAVName', String(255))

	#Relationships
	_ahu = relationship("AHU", back_populates = "_vavs") #Relationship between VAV and AHU
	_hecs = relationship("HEC", back_populates = "_vav") #Relationship between VAV and HEC
	_thermafusers = relationship("Thermafuser", back_populates = "_vav") #Relationship between VAV and Thermafuser
	_vavReadings = relationship("VAVReading", back_populates = "_vav") #Relationship between VAV and VAV_Reading

	#Constructor

	def __init__(self, VAVId, AHUNumber, VAVName, ahu = None, hecs = [], thermafusers = [], VAVReadings = []):

		self._VAVId = VAVId
		self._AHUNumber = AHUNumber
		self._VAVName = VAVName
		self._ahu = ahu
		self._hecs = hecs
		self._VAVReadings = VAVReadings
		self._thermafusers = thermafusers

	#Properties

	@property
	def VAVId(self):
		return self._VAVId

	@VAVId.setter
	def VAVId(self, value):
		self._VAVId = value

	@property
	def VAVName(self):
		return self._VAVName

	@VAVName.setter
	def VAVName(self, value):
		self._VAVName = value

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def ahu(self):
		return self._ahu

	@ahu.setter
	def ahu(self, value):
		self._ahu = value

	@property
	def hecs(self):
		return self._hecs

	@hecs.setter
	def hecs(self, value):
		self._hecs = value

	@property
	def thermafusers(self):
		return self._thermafusers

	@thermafusers.setter
	def thermafusers(self, value):
		self._thermafusers = value

	@property
	def VAVReadings(self):
		return self._VAVReadings

	@VAVReadings.setter
	def VAVReadings(self, value):
		self._VAVReadings = value

	#Methods

	def getComponentName(self):
		return self._VAVName

	def getComponentType(self):
		return "VAV"

	def __str__(self):
		return "<VAV(VAVId = '%d', AHUNumber = '%d', VAVName = '%s')>" % (self._VAVId, self._AHUNumber, self._VAVName)


class VAVReading(Base):
	"""Class to map to the VAV Readings table in the HVAC DB"""

	__tablename__ = 'variable_air_volume_reading'

	_VAVId = Column('VAVId', Integer, ForeignKey("variable_air_volume.VAVId"), primary_key = True)
	_timestamp = Column('Time_stamp', DateTime, primary_key = True)
	_flowInput = Column('FlowInput', Float, nullable=True)
	_zoneTemperature = Column('ZoneTemperature', Float, nullable=True)
	_dischargeTemperature = Column('DischargeTemperature', Float, nullable=True)
	_ductStaticPressure = Column('DuctStaticPressure', String(255), nullable=True)
	_damperPosition = Column('DamperPosition', Float, nullable=True)
	_coolingSetpoint = Column('CoolingSetpoint', Float, nullable=True)
	_heatingSetpoint = Column('HeatingSetpoint', Float, nullable=True)

	#Relationship between SAV Reading and SAV
	_vav = relationship("VAV", back_populates = "_vavReadings", cascade = "all, delete-orphan", single_parent = True)

	#Constructor

	def __init__(self, timestamp = None, VAVId = None, flowInput = None, zoneTemperature = None, dischargeTemperature = None,\
	 ductStaticPressure = None, damperPosition = None, coolingSetpoint = None, heatingSetpoint = None, vav = None):

		self._VAVId = VAVId
		self._timestamp = timestamp
		self._flowInput = flowInput
		self._zoneTemperature = zoneTemperature
		self._dischargeTemperature = dischargeTemperature
		self._ductStaticPressure = ductStaticPressure
		self._damperPosition = damperPosition
		self._coolingSetpoint = coolingSetpoint
		self._heatingSetpoint = heatingSetpoint
		self._vav = vav

	#properties

	@property
	def VAVId(self):
		return self._VAVId

	@VAVId.setter
	def VAVId(self, value):
		self._VAVId = value

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		self._timestamp = value

	@property
	def flowInput(self):
		return self._flowInput

	@flowInput.setter
	def flowInput(self, value):
		self._flowInput = float(value) if value != None else None

	@property
	def zoneTemperature(self):
		return self._zoneTemperature

	@zoneTemperature.setter
	def zoneTemperature(self, value):
		self._zoneTemperature = float(value) if value != None else None

	@property
	def dischargeTemperature(self):
		return self._dischargeTemperature

	@dischargeTemperature.setter
	def dischargeTemperature(self, value):
		self._dischargeTemperature = float(value) if value != None else None

	@property
	def ductStaticPressure(self):
		return self._ductStaticPressure

	@ductStaticPressure.setter
	def ductStaticPressure(self, value):
		self._ductStaticPressure = float(value) if value != None else None

	@property
	def damperPosition(self):
		return self._damperPosition

	@damperPosition.setter
	def damperPosition(self, value):
		self._damperPosition = float(value) if value != None else None

	@property
	def coolingSetpoint(self):
		return self._coolingSetpoint

	@coolingSetpoint.setter
	def coolingSetpoint(self, value):
		self._coolingSetpoint = float(value) if value != None else None

	@property
	def heatingSetpoint(self):
		return self._heatingSetpoint

	@heatingSetpoint.setter
	def heatingSetpoint(self, value):
		self._heatingSetpoint = float(value) if value != None else None

	@property
	def vav(self):
		return self._vav

	@vav.setter
	def vav(self, value):
		self._vav = value

	def to_json(self):

		json_text = {'timestamp': str(datetime.now()), 'flowInput': self._flowInput, 'zoneTemperature': self._zoneTemperature,
					 'dischargeTemperature': self._dischargeTemperature, 'ductStaticPressure': self._ductStaticPressure, 'damperPosition': self._damperPosition,
					 'coolingSetpoint': self._coolingSetpoint, 'heatingSetpoint': self._heatingSetpoint}

		return json_text

	def __str__(self):
		return "<VAVReading(VAVId = '%s', timestamp = '%s', flowInput = '%s', zoneTemperature = '%s', dischargeTemperature = '%s',\
		 ductStaticPressure = '%s',damperPosition = '%s', coolingSetpoint = '%s', heatingSetpoint = '%s')>" \
		% (self._VAVId, str(self._timestamp), self._flowInput, self._zoneTemperature, self._dischargeTemperature,\
		 self._ductStaticPressure, self._damperPosition, self._coolingSetpoint, self._heatingSetpoint)


class Thermafuser(Base):
	"""Class to map to the Thermafuser table in the HVAC DB"""

	__tablename__ = "thermafuser"

	_thermafuserId = Column('ThermafuserId', Integer, primary_key = True, autoincrement = True)
	_AHUNumber = Column('AHUNumber', Integer, ForeignKey("air_handling_unit.AHUNumber"), nullable = True)
	_SAVId = Column('SAVId', Integer, ForeignKey("staged_air_volume.SAVId"), nullable = True)
	_VAVId = Column('VAVId', Integer, ForeignKey("variable_air_volume.VAVId"), nullable = True)
	_thermafuserName = Column('ThermafuserName', Integer)

	#Relationships

	_ahu = relationship("AHU", back_populates = "_thermafusers") #Relationship between Thermafuser and AHU
	_vav = relationship("VAV", back_populates = "_thermafusers") #Relationship between Thermafuser and VAV
	_sav = relationship("SAV", back_populates = "_thermafusers") #Relationship between Thermafuser and SAV
	_thermafuserReadings = relationship("ThermafuserReading", back_populates = "_thermafuser") #Relationship between HEC and HEC_Reading

	#Constructor

	def __init__(self, thermafuserId, thermafuserName, AHUNumber = None, VAVId = None, SAVId = None, ahu = None, vav = None, sav = None, thermafuserReadings = []):
		self._thermafuserName = thermafuserName
		self._AHUNumber = AHUNumber
		self._VAVId = VAVId
		self._SAVId = SAVId
		self._thermafuserId = thermafuserId
		self._ahu = ahu
		self._vav = vav
		self._sav = sav
		self._thermafuserReadings = thermafuserReadings

	#Properties

	@property
	def thermafuserId(self):
		return self._thermafuserId

	@thermafuserId.setter
	def thermafuserId(self, value):
		self._thermafuserId = value

	@property
	def thermafuserName(self):
		return self._thermafuserName

	@thermafuserName.setter
	def thermafuserName(self, value):
		self._thermafuserName = value

	@property
	def AHUNumber(self):
		return self._AHUNumber

	@AHUNumber.setter
	def AHUNumber(self, value):
		self._AHUNumber = value

	@property
	def VAVId(self):
		return self._VAVId

	@VAVId.setter
	def VAVId(self, value):
		self._VAVId = value

	@property
	def SAVId(self):
		return self._SAVId

	@SAVId.setter
	def SAVId(self, value):
		self._SAVId = value

	@property
	def ahu(self):
		return self._ahu

	@ahu.setter
	def ahu(self, value):
		self._ahu = value

	@property
	def vav(self):
		return self._vav

	@vav.setter
	def vav(self, value):
		self._vav = value

	@property
	def sav(self):
		return self._sav

	@sav.setter
	def sav(self, value):
		self._sav = value

	@property
	def thermafuserReadings(self):
		return self._thermafuserReadings

	@thermafuserReadings.setter
	def thermafuserReadings(self, value):
		self._thermafuserReadings = value

	#Methods

	def getComponentName(self):
		return self._thermafuserName

	def getComponentType(self):
		return "Thermafuser"

	def __str__(self):
		return "<Thermafuser(thermafuserId = '%d', AHUNumber = '%s', SAVId = '%s', VAVId = '%s', thermafuserName = '%s')>" \
		% (self._thermafuserId, str(self._AHUNumber), str(self._SAVId), str(self._VAVId), str(self._thermafuserName))


class ThermafuserReading(Base):
	"""Class to map to the Thermafuser Readings table in the HVAC DB"""

	__tablename__ = 'thermafuser_reading'

	_timestamp = Column('Time_stamp', DateTime, primary_key = True)
	_thermafuserId = Column('ThermafuserId', Integer, ForeignKey("thermafuser.ThermafuserId"), primary_key = True)
	_roomOccupied = Column('RoomOccupied', Boolean, nullable=True)
	_zoneTemperature = Column('ZoneTemperature', Float, nullable=True)
	_supplyAir = Column('SupplyAir', Float, nullable=True)
	_airflowFeedback = Column('AirflowFeedback', Float, nullable=True)
	_occupiedCoolingSetpoint = Column('OccupiedCoolingSetpoint', Float, nullable=True)
	_occupiedHeatingSetpoint = Column('OccupiedHeatingSetpoint', Float, nullable=True)
	_terminalLoad = Column('TerminalLoad', Float, nullable=True)

	#Relationship between Thermafuser Reading and Thermafuser
	_thermafuser = relationship("Thermafuser", back_populates = "_thermafuserReadings",  cascade = "all, delete-orphan", single_parent = True)

	#Constructor

	def __init__(self, timestamp = None, thermafuserId = None, roomOccupied = None, zoneTemperature = None, supplyAir = None, airflowFeedback = None, \
		occupiedCoolingSetpoint = None, occupiedHeatingSetpoint = None, terminalLoad = None, thermafuser = None):

		self._thermafuserId = thermafuserId
		self._timestamp = timestamp
		self._roomOccupied = roomOccupied
		self._zoneTemperature = zoneTemperature
		self._supplyAir = supplyAir
		self._airflowFeedback = airflowFeedback
		self._occupiedCoolingSetpoint = occupiedCoolingSetpoint
		self._occupiedHeatingSetpoint = occupiedHeatingSetpoint
		self._terminalLoad = terminalLoad
		self._thermafuser = thermafuser

	#properties

	@property
	def thermafuserId(self):
		return self._thermafuserId

	@thermafuserId.setter
	def thermafuserId(self, value):
		self._thermafuserId = value

	@property
	def timestamp(self):
		return self._timestamp

	@timestamp.setter
	def timestamp(self, value):
		self._timestamp = value

	@property
	def roomOccupied(self):
		return self._roomOccupied

	@roomOccupied.setter
	def roomOccupied(self, value):
		self._roomOccupied = bool(value) if value != None else None

	@property
	def zoneTemperature(self):
		return self._zoneTemperature

	@zoneTemperature.setter
	def zoneTemperature(self, value):
		self._zoneTemperature = float(value) if value != None else None

	@property
	def supplyAir(self):
		return self._supplyAir

	@supplyAir.setter
	def supplyAir(self, value):
		self._supplyAir = float(value) if value != None else None

	@property
	def airflowFeedback(self):
		return self._airflowFeedback

	@airflowFeedback.setter
	def airflowFeedback(self, value):
		self._airflowFeedback = float(value) if value != None else None

	@property
	def occupiedCoolingSetpoint(self):
		return self._occupiedCoolingSetpoint

	@occupiedCoolingSetpoint.setter
	def occupiedCoolingSetpoint(self, value):
		self._occupiedCoolingSetpoint = float(value) if value != None else None

	@property
	def occupiedHeatingSetpoint(self):
		return self._occupiedHeatingSetpoint

	@occupiedHeatingSetpoint.setter
	def occupiedHeatingSetpoint(self, value):
		self._occupiedHeatingSetpoint = float(value) if value != None else None

	@property
	def terminalLoad(self):
		return self._terminalLoad

	@terminalLoad.setter
	def terminalLoad(self, value):
		self._terminalLoad = float(value) if value != None else None

	@property
	def thermafuser(self):
		return self._thermafuser

	@thermafuser.setter
	def thermafuser(self, value):
		self._thermafuser = value

	def to_json(self):

		json_text = {'timestamp': str(datetime.now()), 'roomOccupied': self._roomOccupied, 'zoneTemperature': self._zoneTemperature,
					 'supplyAir': self._supplyAir, 'airflowFeedback': self._airflowFeedback, 'occupiedCoolingSetpoint': self._occupiedCoolingSetpoint,
					 'occupiedHeatingSetpoint': self._occupiedHeatingSetpoint, 'terminalLoad': self._terminalLoad}

		return json_text

	def __str__(self):
		return "<ThermafuserReading(thermafuserId = '%s', timestamp = '%s', roomOccupied = '%s', zoneTemperature = '%s', supplyAir = '%s', airflowFeedback = '%s',\
		occupiedCoolingSetpoint = '%s', occupiedHeatingSetpoint = '%s', terminalLoad = '%s')>" \
		% (self._thermafuserId, str(self._timestamp), self._roomOccupied, self._zoneTemperature, self._supplyAir, self._airflowFeedback, self._occupiedCoolingSetpoint,\
		  self._occupiedHeatingSetpoint, self._terminalLoad)

	def __str2__(self):
		return "<ThermafuserReading(thermafuserId = '%s', timestamp = '%s')>" % (self._thermafuserId, str(self._timestamp))












