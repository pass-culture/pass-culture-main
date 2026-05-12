import { mutate } from 'swr'

import { apiNew } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'
import { toBody } from './toBody'

export const saveVenueSettings = async (
  formValues: VenueSettingsFormValues,
  formContext: VenueSettingsFormContext,
  { venue }: { venue: GetVenueResponseModel }
) => {
  await apiNew.editVenue({
    path: { venue_id: Number(venue.id) },
    body: toBody(formValues, formContext),
  })
  await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])
}
