from enum import Enum
class ConstraintType(Enum):		#define constraint type of each constraint
	NOT_NULL = 1
	UNIQUE = 2
	PRIMARY_KEY = 3
	FOREIGN_KEY = 4