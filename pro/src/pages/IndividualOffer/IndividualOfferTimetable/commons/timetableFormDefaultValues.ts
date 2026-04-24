import { HasDateEnum, type IndividualOfferTimetableFormValues } from './types'

export const timetableFormDefaultValues = {
  hasStartDate: HasDateEnum.NO,
  hasEndDate: HasDateEnum.NO,
  startDate: null,
  endDate: null,
} satisfies IndividualOfferTimetableFormValues
