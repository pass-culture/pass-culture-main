import { AccessibiltyFormValues } from 'core/shared'

export interface VenueEditionFormValues {
  accessibility: AccessibiltyFormValues
  description: string
  email: string | null
  isAccessibilityAppliedOnAllOffers: boolean
  phoneNumber: string | null
  venueLabel: string | null
  webSite: string | null
}
