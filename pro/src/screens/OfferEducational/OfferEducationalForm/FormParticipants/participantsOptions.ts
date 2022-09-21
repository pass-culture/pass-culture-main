import { StudentLevels } from 'apiClient/v1'

export const participantsOptions = [
  { label: 'Tout sélectionner', name: 'participants.all' },
  ...Object.values(StudentLevels).map(studentLevel => ({
    label: studentLevel,
    name: `participants.${studentLevel}`,
  })),
]
