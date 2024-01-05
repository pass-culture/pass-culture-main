import { StudentLevels } from 'apiClient/adage'

import { buildStudentLevelsMapWithDefaultValue } from '../buildStudentLevelsMapWithDefaultValue'

describe('buildStudentLevelsMapWithDefaultValue', () => {
  it('should return the students level map with all keys enabled', () => {
    const studentsMap = buildStudentLevelsMapWithDefaultValue(true)
    expect(
      Object.values(studentsMap).reduce((prev, curr) => prev && curr, true)
    ).toBeTruthy()
  })

  it('should return the students level map with all keys disabled', () => {
    const studentsMap = buildStudentLevelsMapWithDefaultValue(false)
    expect(
      Object.values(studentsMap).reduce((prev, curr) => prev || curr, false)
    ).toBeFalsy()
  })

  it('should return the students level map with specific keys enabled', () => {
    const studentsMap = buildStudentLevelsMapWithDefaultValue(
      (key) => key === StudentLevels.COLL_GE_3E
    )
    expect(studentsMap[StudentLevels.COLL_GE_3E]).toBeTruthy()
    expect(studentsMap[StudentLevels.CAP_1RE_ANN_E]).toBeFalsy()
    expect(studentsMap[StudentLevels.LYC_E_SECONDE]).toBeFalsy()
  })

  it('should return the students levels without marseille levels', () => {
    const studentsMap = buildStudentLevelsMapWithDefaultValue(true)
    expect(
      studentsMap[StudentLevels._COLES_INNOVANTES_MARSEILLE_EN_GRAND_L_MENTAIRE]
    ).toBeFalsy()
  })

  it('should return the students levels with marseille levels', () => {
    const studentsMap = buildStudentLevelsMapWithDefaultValue(true, true)
    expect(
      studentsMap[StudentLevels._COLES_INNOVANTES_MARSEILLE_EN_GRAND_L_MENTAIRE]
    ).toBeTruthy()
  })
})
