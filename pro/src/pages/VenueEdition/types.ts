import { AccessibiltyFormValues } from 'core/shared'

type DayValues = {
  morningStartingHour: string
  morningEndingHour: string
  afternoonStartingHour: string
  afternoonEndingHour: string
}

export interface VenueEditionFormValues {
  accessibility: AccessibiltyFormValues
  description: string
  email: string | null
  isAccessibilityAppliedOnAllOffers: boolean
  phoneNumber: string | null
  webSite: string | null
  days: string[]
  monday: DayValues
  tuesday: DayValues
  wednesday: DayValues
  thursday: DayValues
  friday: DayValues
  saturday: DayValues
  sunday: DayValues
}
