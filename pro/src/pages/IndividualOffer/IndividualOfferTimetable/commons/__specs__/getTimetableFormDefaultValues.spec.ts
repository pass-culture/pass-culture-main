import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'

import { getTimetableFormDefaultValues } from '../getTimetableFormDefaultValues'

const defaultOpeningHours: WeekdayOpeningHoursTimespans = {
  MONDAY: null,
  TUESDAY: null,
  WEDNESDAY: null,
  THURSDAY: null,
  FRIDAY: null,
  SATURDAY: null,
  SUNDAY: null,
}

describe('getTimetableFormDefaultValues', () => {
  it('should get the default values for an empty form in creation mode', () => {
    expect(
      getTimetableFormDefaultValues({
        openingHours: defaultOpeningHours,
        isOhoFFEnabled: true,
      })
    ).toEqual(
      expect.objectContaining({
        openingHours: defaultOpeningHours,
        timetableType: 'calendar',
      })
    )
  })

  it('should set the initial form as calendar type if there are stocks already', () => {
    expect(
      getTimetableFormDefaultValues({
        openingHours: defaultOpeningHours,
        isOhoFFEnabled: true,
      })
    ).toEqual(
      expect.objectContaining({
        timetableType: 'calendar',
      })
    )
  })

  it('should set the initial form as openingHours type if there are non-empty openingHours already', () => {
    expect(
      getTimetableFormDefaultValues({
        openingHours: { ...defaultOpeningHours, MONDAY: [['12:12', '15:15']] },
        isOhoFFEnabled: true,
      })
    ).toEqual(
      expect.objectContaining({
        timetableType: 'openingHours',
      })
    )
  })
})
