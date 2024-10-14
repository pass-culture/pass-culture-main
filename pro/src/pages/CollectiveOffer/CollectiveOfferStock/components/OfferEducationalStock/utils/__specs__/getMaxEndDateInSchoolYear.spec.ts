import { getMaxEndDateInSchoolYear } from '../getMaxEndDateInSchoolYear'

describe('getMaxEndDate', () => {
  it('should returns 31st of August of next year if current date is after September', () => {
    const result = getMaxEndDateInSchoolYear('2024-09-01')
    expect(result).toEqual(new Date(2025, 7, 31))
  })

  it('returns 31st August of current year if current date is before September', () => {
    const result = getMaxEndDateInSchoolYear('2024-08-01')
    expect(result).toEqual(new Date(2024, 7, 31))
  })
})
