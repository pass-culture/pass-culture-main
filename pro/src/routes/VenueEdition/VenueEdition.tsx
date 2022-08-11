import React from 'react'
import { useHistory, useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { useGetVenue } from 'core/Venue'
import { useHomePath } from 'hooks'
import { setInitialFormValues } from 'new_components/VenueForm'
import { VenueEdition as VenueEditionScreen } from 'screens/VenueEdition'

const VenueEdition = (): JSX.Element | null => {
  const homePath = useHomePath()
  const { venueId } = useParams<{ venueId: string }>()
  const notify = useNotification()
  const history = useHistory()

  const { isLoading, error, data: venue } = useGetVenue(venueId)

  if (isLoading === true) {
    return <Spinner />
  }

  if (error !== undefined) {
    notify.error(error.message)
    history.push(homePath)
    return null
  }

  const initialValues = setInitialFormValues(venue)
  return <VenueEditionScreen initialValues={initialValues} />
}

export default VenueEdition
