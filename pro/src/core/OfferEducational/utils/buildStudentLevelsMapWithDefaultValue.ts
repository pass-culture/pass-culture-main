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
        StudentLevels._COLES_INNOVANTES_MARSEILLE_EN_GRAND_L_MENTAIRE,
        StudentLevels._COLES_INNOVANTES_MARSEILLE_EN_GRAND_MATERNELLE,
      ].includes(level)
    ) {
      continue
    }

    mappedLavels[level] = typeof value === 'boolean' ? value : value(level)
  }
  return mappedLavels
}
