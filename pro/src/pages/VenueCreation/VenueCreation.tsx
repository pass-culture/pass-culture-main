import React from 'react'
import { Navigate, useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import { useGetVenueTypes } from 'core/Venue/adapters/getVenueTypeAdapter'
import useNotification from 'hooks/useNotification'
import { DEFAULT_FORM_VALUES } from 'pages/VenueCreation/constants'
import { GET_OFFERER_QUERY_KEY } from 'pages/VenueSettings/VenueSettings'
import Spinner from 'ui-kit/Spinner/Spinner'

import { VenueCreationFormScreen } from './VenueCreationFormScreen'

export const VenueCreation = (): JSX.Element | null => {
  const homePath = '/accueil'
  const { offererId } = useParams<{ offererId: string }>()
  const notify = useNotification()

  const initialValues = { ...DEFAULT_FORM_VALUES }

  const offererQuery = useSWR(
    [GET_OFFERER_QUERY_KEY, offererId],
    ([, offererIdParam]) => api.getOfferer(Number(offererIdParam))
  )
  const offerer = offererQuery.data

  const {
    isLoading: isLoadingVenueTypes,
    error: errorVenueTypes,
    data: venueTypes,
  } = useGetVenueTypes()

  if (offererQuery.error || errorVenueTypes) {
    const loadingError = [offererQuery.error, errorVenueTypes].find(
      (error) => error !== undefined
    )
    if (loadingError !== undefined) {
      notify.error(loadingError.message)
    }
    return <Navigate to={homePath} />
  }

  if (!offerer) {
    return null
  }

  return (
    <AppLayout layout={'sticky-actions'}>
      {offererQuery.isLoading || isLoadingVenueTypes ? (
        <Spinner />
      ) : (
        <VenueCreationFormScreen
          initialValues={initialValues}
          offerer={offerer}
          venueTypes={venueTypes}
        />
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueCreation
