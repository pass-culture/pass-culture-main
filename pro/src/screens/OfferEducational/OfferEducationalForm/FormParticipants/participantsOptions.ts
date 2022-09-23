import { StudentLevels } from 'apiClient/v1'

export const ALL_STUDENTS_LABEL = 'Tout sélectionner'

export const participantsOptions = [
  { label: ALL_STUDENTS_LABEL, name: 'participants.all' },
  ...Object.values(StudentLevels).map(studentLevel => ({
    label: studentLevel,
    name: `participants.${studentLevel}`,
  })),
]
