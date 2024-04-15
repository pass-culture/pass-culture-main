import React from 'react'
import { useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import { DEFAULT_FORM_VALUES } from 'pages/VenueCreation/constants'
import { GET_OFFERER_QUERY_KEY } from 'pages/VenueSettings/VenueSettings'
import Spinner from 'ui-kit/Spinner/Spinner'

import { VenueCreationFormScreen } from './VenueCreationFormScreen'

export const VenueCreation = (): JSX.Element | null => {
  const { offererId } = useParams<{ offererId: string }>()

  const initialValues = { ...DEFAULT_FORM_VALUES }

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, offererId],
    ([, offererIdParam]) => api.getOfferer(Number(offererIdParam))
  )
  const offerer = offererQuery.data

  const { isLoading: isLoadingVenueTypes, data: venueTypes } =
    useGetVenueTypes()

  if (
    offererQuery.isLoading ||
    isLoadingVenueTypes ||
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
