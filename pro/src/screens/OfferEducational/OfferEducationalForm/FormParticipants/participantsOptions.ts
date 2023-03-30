import { StudentLevels } from 'apiClient/v1'

export const ALL_STUDENTS_LABEL = 'Tout sélectionner'

const getStudentLevelLabel = (studentLevel: StudentLevels) => {
  switch (studentLevel) {
    case StudentLevels.COLL_GE_6E:
    case StudentLevels.COLL_GE_5E:
      return `${studentLevel} : à partir de septembre 2023`
    default:
      return studentLevel
  }
}

export const participantsOptions = [
  { label: ALL_STUDENTS_LABEL, name: 'participants.all' },
  ...Object.values(StudentLevels).map(studentLevel => ({
    label: getStudentLevelLabel(studentLevel),
    name: `participants.${studentLevel}`,
  })),
]
