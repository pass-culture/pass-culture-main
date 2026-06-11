import { apiNew } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1/new'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'
import { toBody } from './toBody'

export const saveVenueSettings = async (
  formValues: VenueSettingsFormValues,
  formContext: VenueSettingsFormContext,
  { venue }: { venue: GetVenueResponseModel }
): Promise<GetVenueResponseModel> => {
  return await apiNew.editVenue({
    path: { venue_id: Number(venue.id) },
    body: toBody(formValues, formContext),
  })
}
