import { AccessibilityFormValues } from '@/commons/core/shared/types'

export type DayValues = {
  morningStartingHour: string
  morningEndingHour: string
  afternoonStartingHour: string
  afternoonEndingHour: string
  isAfternoonOpen: boolean
}

export interface VenueEditionFormValues {
  accessibility: AccessibilityFormValues
  description: string
  email: string | null
  isAccessibilityAppliedOnAllOffers: boolean
  phoneNumber: string | null
  webSite: string | null
  isOpenToPublic: string | null
  days: Day[]
  monday?: DayValues
  tuesday?: DayValues
  wednesday?: DayValues
  thursday?: DayValues
  friday?: DayValues
  saturday?: DayValues
  sunday?: DayValues
}

export type Day =
  | 'monday'
  | 'tuesday'
  | 'wednesday'
  | 'thursday'
  | 'friday'
  | 'saturday'
  | 'sunday'
