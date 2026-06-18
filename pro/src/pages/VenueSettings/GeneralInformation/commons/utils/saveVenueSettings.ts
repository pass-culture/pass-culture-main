import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'

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
  return await api.editVenue({
    path: { venue_id: Number(venue.id) },
    body: toBody(formValues, formContext),
  })
}
