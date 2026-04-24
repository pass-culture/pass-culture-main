import { areOpeningHoursEmpty } from '../areOpeningHoursEmpty'

describe('areOpeningHoursEmpty', () => {
  it('should assert if at least one of the days have opening hours', () => {
    expect(areOpeningHoursEmpty()).toEqual(true)
    expect(areOpeningHoursEmpty(null)).toEqual(true)
    expect(areOpeningHoursEmpty({})).toEqual(true)
    expect(areOpeningHoursEmpty({ MONDAY: null, TUESDAY: null })).toEqual(true)
    expect(areOpeningHoursEmpty({ MONDAY: null, TUESDAY: [] })).toEqual(true)
    expect(
      areOpeningHoursEmpty({ MONDAY: null, TUESDAY: [['10:10', '22:22']] })
    ).toEqual(false)
  })
})
