import type {
  GetVenueResponseModel,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'

import { getTimetableDefaultOpeningHours } from '../getTimetableDefaultOpeningHours'

const defaultOfferOpeningHours: WeekdayOpeningHoursTimespans = {
  MONDAY: null,
  TUESDAY: null,
  WEDNESDAY: null,
  THURSDAY: null,
  FRIDAY: null,
  SATURDAY: null,
  SUNDAY: null,
}

const defaultVenueOpeningHours: GetVenueResponseModel['openingHours'] = {
  MONDAY: null,
  TUESDAY: null,
  WEDNESDAY: null,
  THURSDAY: null,
  FRIDAY: null,
  SATURDAY: null,
  SUNDAY: null,
}

describe('getTimetableDefaultOpeningHours', () => {
  it('should return the offer opening hours if they are not empty', () => {
    expect(
      getTimetableDefaultOpeningHours({
        offerOpeningHours: {
          ...defaultOfferOpeningHours,
          MONDAY: [['10:10', '11:11']],
        },
        venueOpeningHours: {
          ...defaultVenueOpeningHours,
          MONDAY: [['17:12', '19:22']],
        },
      })
    ).toEqual(expect.objectContaining({ MONDAY: [['10:10', '11:11']] }))
  })

  it('should return the venue opening hours if the offer opening hours are empty', () => {
    expect(
      getTimetableDefaultOpeningHours({
        offerOpeningHours: defaultOfferOpeningHours,
        venueOpeningHours: {
          ...defaultVenueOpeningHours,
          MONDAY: [['17:12', '19:22']],
        },
      })
    ).toEqual(expect.objectContaining({ MONDAY: [['17:12', '19:22']] }))
  })
})
