import { GetVenueResponseModel } from 'apiClient/v1'
import { AccessibilityEnum } from 'commons/core/shared/types'
import { DEFAULT_INTITIAL_OPENING_HOURS } from 'pages/VenueCreation/constants'

import { DayValues, VenueEditionFormValues, Day } from './types'

export const setInitialFormValues = (
  venue: GetVenueResponseModel
): VenueEditionFormValues => {
  return {
    accessibility: {
      [AccessibilityEnum.VISUAL]: venue.visualDisabilityCompliant || false,
      [AccessibilityEnum.MENTAL]: venue.mentalDisabilityCompliant || false,
      [AccessibilityEnum.AUDIO]: venue.audioDisabilityCompliant || false,
      [AccessibilityEnum.MOTOR]: venue.motorDisabilityCompliant || false,
      [AccessibilityEnum.NONE]: [
        venue.visualDisabilityCompliant,
        venue.mentalDisabilityCompliant,
        venue.audioDisabilityCompliant,
        venue.motorDisabilityCompliant,
      ].every((accessibility) => accessibility === false),
    },
    description: venue.description || '',
    email: venue.contact?.email || '',
    isAccessibilityAppliedOnAllOffers: false,
    phoneNumber: venue.contact?.phoneNumber || '',
    webSite: venue.contact?.website || '',
    ...buildOpeningHoursValues(venue.openingHours),
  }
}

function buildOpeningHoursValues(
  openingHours: GetVenueResponseModel['openingHours']
) {
  const filledDays = Object.entries(openingHours ?? {}).filter((dateAndHour) =>
    Boolean(dateAndHour[1])
  )

  if (!openingHours) {
    return { days: [] }
  }
  const days = filledDays.map((dateAndHour) =>
    dateAndHour[0].toLowerCase()
  ) as Day[]

  const monday = buildHourOfDay(openingHours.MONDAY)
  const tuesday = buildHourOfDay(openingHours.TUESDAY)
  const wednesday = buildHourOfDay(openingHours.WEDNESDAY)
  const thursday = buildHourOfDay(openingHours.THURSDAY)
  const friday = buildHourOfDay(openingHours.FRIDAY)
  const saturday = buildHourOfDay(openingHours.SATURDAY)
  const sunday = buildHourOfDay(openingHours.SUNDAY)

  return {
    days,
    monday,
    tuesday,
    wednesday,
    thursday,
    friday,
    saturday,
    sunday,
  }
}

function buildHourOfDay(
  dayOpeningHour: Record<string, any> | undefined
): DayValues {
  return dayOpeningHour
    ? {
        morningStartingHour: Object.values(dayOpeningHour)[0].open,
        morningEndingHour: Object.values(dayOpeningHour)[0].close,
        afternoonStartingHour: Object.values(dayOpeningHour)[1]
          ? Object.values(dayOpeningHour)[1].open
          : '',
        afternoonEndingHour: Object.values(dayOpeningHour)[1]
          ? Object.values(dayOpeningHour)[1].close
          : '',
        isAfternoonOpen: Object.values(dayOpeningHour)[1] ? true : false,
      }
    : { ...DEFAULT_INTITIAL_OPENING_HOURS }
}
