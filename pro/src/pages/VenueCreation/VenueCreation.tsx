import { useSelector } from 'react-redux'
import { useNavigate, useParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import {
  GET_OFFERER_QUERY_KEY,
  GET_VENUE_TYPES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { DEFAULT_FORM_VALUES } from 'pages/VenueCreation/constants'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { VenueCreationFormScreen } from './VenueCreationFormScreen'

export const VenueCreation = (): JSX.Element | null => {
  const navigate = useNavigate()
  const { offererId } = useParams<{ offererId: string }>()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  if (selectedOffererId && selectedOffererId.toString() !== offererId) {
    // Prevents the following error
    // Cannot update a component (`RouterProvider`) while rendering a different component (`VenueCreation`).
    // As this is a temporary thing, it should be ok to keep until the beta is done
    setTimeout(() => {
      navigate(`/structures/${selectedOffererId}/lieux/creation`)
    })
  }

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
      <Layout>
        <Spinner />
      </Layout>
    )
  }

  return (
    <Layout layout={'sticky-actions'}>
      <VenueCreationFormScreen
        initialValues={initialValues}
        offerer={offerer}
        venueTypes={venueTypes}
      />
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = VenueCreation
