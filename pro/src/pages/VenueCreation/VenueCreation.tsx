import React from 'react'
import { useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import {
  GET_OFFERER_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'config/swrQueryKeys'
import { DEFAULT_FORM_VALUES } from 'pages/VenueCreation/constants'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { VenueCreationFormScreen } from './VenueCreationFormScreen'

export const VenueCreation = (): JSX.Element | null => {
  const { offererId } = useParams<{ offererId: string }>()

  const initialValues = { ...DEFAULT_FORM_VALUES }

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, offererId],
    ([, offererIdParam]) => api.getOfferer(Number(offererIdParam))
  )
  const offerer = offererQuery.data

  const venueTypesQuery = useSWR([GET_VENUE_TYPES_QUERY_KEY], () =>
    api.getVenueTypes()
  )
  const venueTypes = venueTypesQuery.data

  if (
    offererQuery.isLoading ||
    venueTypesQuery.isLoading ||
    !offerer ||
    !venueTypes
  ) {
    return (
      <AppLayout>
        <Spinner />
      </AppLayout>
    )
  }

  return (
    <AppLayout layout={'sticky-actions'}>
      <VenueCreationFormScreen
        initialValues={initialValues}
        offerer={offerer}
        venueTypes={venueTypes}
      />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueCreation
