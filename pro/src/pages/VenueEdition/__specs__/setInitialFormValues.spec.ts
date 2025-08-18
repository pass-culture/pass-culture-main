import type { GetVenueResponseModel } from '@/apiClient/v1'

import { getOpeningHoursFromGetVenueResponseOpeningHours } from '../setInitialFormValues'

const DEFAULT_OPENING_HOURS: GetVenueResponseModel['openingHours'] = {
  MONDAY: [
    { open: '12:12', close: '14:14' },
    { open: '15:15', close: '16:16' },
  ],
  TUESDAY: [{ open: '12:12', close: '14:14' }],
  THURSDAY: [],
  WEDNESDAY: null,
  FRIDAY: null,
  SATURDAY: null,
  SUNDAY: null,
}

describe('getOpeningHoursFromGetVenueResponseOpeningHours', () => {
  it('should transform the opening hours received from the venue into the opening hours model used everywhere else', () => {
    expect(getOpeningHoursFromGetVenueResponseOpeningHours(null)).toEqual(null)

    expect(
      getOpeningHoursFromGetVenueResponseOpeningHours(DEFAULT_OPENING_HOURS)
    ).toEqual({
      MONDAY: [
        ['12:12', '14:14'],
        ['15:15', '16:16'],
      ],
      TUESDAY: [['12:12', '14:14']],
      THURSDAY: null,
      WEDNESDAY: null,
      FRIDAY: null,
      SATURDAY: null,
      SUNDAY: null,
    })
  })
})
