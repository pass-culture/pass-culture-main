import { StudentLevels } from 'apiClient/v1'

export const buildStudentLevelsMapWithDefaultValue = (
  value: boolean | ((studentKey: StudentLevels) => boolean)
): Record<StudentLevels, boolean> =>
  Object.values(StudentLevels).reduce(
    (studentsMapping, studentKey) => {
      studentsMapping[studentKey] =
        typeof value === 'boolean' ? value : value(studentKey)
      return studentsMapping
    },
    {} as Record<StudentLevels, boolean>
  )
