import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import type { PartialBy } from '@/commons/utils/types'

import type { VenueSettingsFormContext } from '../types'
import type { VenueSettingsFormValuesType } from '../validationSchema'
import { toBody } from './toBody'

export const saveVenueSettings = async (
  formValues: PartialBy<VenueSettingsFormValuesType, 'venueType'>,
  formContext: VenueSettingsFormContext,
  { venue }: { venue: GetVenueResponseModel }
) => {
  await api.editVenue(venue.id, toBody(formValues, formContext))
  await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])
}
