import { StudentLevels } from '@/apiClient//v1'
import { DEFAULT_MARSEILLE_STUDENTS } from '@/commons/core/shared/constants'

export const buildStudentLevelsMapWithDefaultValue = (
  value: boolean | ((studentKey: StudentLevels) => boolean),
  isMarseilleEnabled?: boolean
): Record<StudentLevels, boolean> => {
  const mappedLavels = {} as Record<StudentLevels, boolean>

  for (const level of Object.values(StudentLevels)) {
    if (!isMarseilleEnabled && DEFAULT_MARSEILLE_STUDENTS.includes(level)) {
      continue
    }

    mappedLavels[level] = typeof value === 'boolean' ? value : value(level)
  }
  return mappedLavels
}
