import type { PartialBy, VenueSettingsFormValues } from '../types'

export const removeVenueTypeFieldIf =
  (condition: boolean) =>
  (formValues: PartialBy<VenueSettingsFormValues, 'venueType'>) => {
    const { venueType: _, ...props } = formValues
    if (condition) {
      return props
    }
    return formValues
  }
