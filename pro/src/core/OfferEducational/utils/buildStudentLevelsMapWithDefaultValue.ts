import { StudentLevels } from 'apiClient/v1'

export const buildStudentLevelsMapWithDefaultValue = (
  value: boolean | ((studentKey: StudentLevels) => boolean),
  isMarseilleEnabled?: boolean
): Record<StudentLevels, boolean> => {
  const mappedLavels = {} as Record<StudentLevels, boolean>

  for (const level of Object.values(StudentLevels)) {
    if (
      !isMarseilleEnabled &&
      [
        StudentLevels._COLES_MARSEILLE_MATERNELLE,
        StudentLevels._COLES_MARSEILLE_CP_CE1_CE2,
        StudentLevels._COLES_MARSEILLE_CM1_CM2,
      ].includes(level)
    ) {
      continue
    }

    mappedLavels[level] = typeof value === 'boolean' ? value : value(level)
  }
  return mappedLavels
}
