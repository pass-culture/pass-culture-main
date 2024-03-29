import React from 'react'
import { useLocation } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { BannerCreateOfferAdmin } from 'components/Banner'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import useCurrentUser from 'hooks/useCurrentUser'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import InformationsScreen from 'screens/IndividualOffer/InformationsScreen/InformationsScreen'
import Spinner from 'ui-kit/Spinner/Spinner'
import { parse } from 'utils/query-string'

const GET_VENUES_QUERY_KEY = 'getVenues'
const GET_OFFERER_NAMES_QUERY_KEY = 'getOffererNames'

export const Offer = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { currentUser } = useCurrentUser()
  const { offer } = useIndividualOfferContext()

  const { search } = useLocation()
  const { structure: offererId, lieu: venueId } = parse(search)

  const shouldNotFetchVenues = currentUser.isAdmin && !offererId

  const venuesQuery = useSWR(
    () => (shouldNotFetchVenues ? null : [GET_VENUES_QUERY_KEY, offererId]),
    ([, offererId]) => api.getVenues(null, true, Number(offererId)),
    { fallbackData: { venues: [] } }
  )
  const offererNamesQuery = useSWR(
    [GET_OFFERER_NAMES_QUERY_KEY, offererId],
    ([, offererId]) => api.listOfferersNames(null, null, Number(offererId)),
    { fallbackData: { offerersNames: [] } }
  )

  const showAdminCreationBanner =
    currentUser.isAdmin &&
    mode === OFFER_WIZARD_MODE.CREATION &&
    !(offererId || offer)

  if (venuesQuery.isLoading || offererNamesQuery.isLoading) {
    return <Spinner />
  }
  venuesQuery.data
  return (
    <IndivualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      {showAdminCreationBanner ? (
        <BannerCreateOfferAdmin />
      ) : (
        <InformationsScreen
          offererId={offererId}
          venueId={venueId}
          venueList={venuesQuery.data.venues}
          offererNames={offererNamesQuery.data.offerersNames}
        />
      )}
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Offer
