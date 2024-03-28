import { GetVenueResponseModel, VenueListItemResponseModel } from 'apiClient/v1'
import { AccessiblityEnum } from 'core/shared'
import { DEFAULT_INTITIAL_OPENING_HOURS } from 'pages/VenueCreation/constants'

import { DayValues, VenueEditionFormValues, Day } from './types'

export const buildAccessibilityFormValues = (
  venue: GetVenueResponseModel | VenueListItemResponseModel
) => {
  return {
    [AccessiblityEnum.VISUAL]: venue.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: venue.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: venue.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: venue.motorDisabilityCompliant || false,
    [AccessiblityEnum.NONE]: [
      venue.visualDisabilityCompliant,
      venue.mentalDisabilityCompliant,
      venue.audioDisabilityCompliant,
      venue.motorDisabilityCompliant,
    ].every((accessibility) => accessibility === false),
  }
}

export const setInitialFormValues = (
  venue: GetVenueResponseModel
): VenueEditionFormValues => {
  return {
    accessibility: buildAccessibilityFormValues(venue),
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

  if (!openingHours || openingHours.length === 0) {
    return {
      days: [],
      monday: DEFAULT_INTITIAL_OPENING_HOURS,
      tuesday: DEFAULT_INTITIAL_OPENING_HOURS,
      wednesday: DEFAULT_INTITIAL_OPENING_HOURS,
      thursday: DEFAULT_INTITIAL_OPENING_HOURS,
      friday: DEFAULT_INTITIAL_OPENING_HOURS,
      saturday: DEFAULT_INTITIAL_OPENING_HOURS,
      sunday: DEFAULT_INTITIAL_OPENING_HOURS,
    }
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
    : DEFAULT_INTITIAL_OPENING_HOURS
}
