import { useSelector } from 'react-redux'
import { useSearchParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  GET_OFFERER_NAMES_QUERY_KEY,
  GET_VENUES_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useCurrentUser } from 'commons/hooks/useCurrentUser'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { BannerCreateOfferAdmin } from 'components/Banner/BannerCreateOfferAdmin'
import { IndivualOfferLayout } from 'components/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'components/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { InformationsScreen } from 'components/IndividualOffer/InformationsScreen/InformationsScreen'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const Offer = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { currentUser } = useCurrentUser()
  const { offer } = useIndividualOfferContext()
  const [searchParams] = useSearchParams()

  let venueId = searchParams.get('lieu')
  const selectedOffererId = useSelector(selectCurrentOffererId)

  // At first we look for the offerer id in the offer,
  // else we look for the selected offerer id in the redux store
  const offererId = offer?.venue.managingOfferer.id ?? selectedOffererId

  const shouldNotFetchVenues = currentUser.isAdmin && !offererId

  const venuesQuery = useSWR(
    () => (shouldNotFetchVenues ? null : [GET_VENUES_QUERY_KEY, offererId]),
    ([, offererIdParam]) => api.getVenues(null, true, offererIdParam),
    { fallbackData: { venues: [] } }
  )
  const offererNamesQuery = useSWR(
    [GET_OFFERER_NAMES_QUERY_KEY, offererId],
    ([, offererIdParam]) => api.listOfferersNames(null, null, offererIdParam),
    { fallbackData: { offerersNames: [] } }
  )

  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const showAdminCreationBanner =
    currentUser.isAdmin &&
    mode === OFFER_WIZARD_MODE.CREATION &&
    !(offererId || offer)

  if (venuesQuery.isLoading || offererNamesQuery.isLoading) {
    return <Spinner />
  }

  if (venueId === null && isOfferAddressEnabled) {
    venueId = String(venuesQuery.data.venues[0].id)
  }

  return (
    <IndivualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      {showAdminCreationBanner ? (
        <BannerCreateOfferAdmin />
      ) : (
        <InformationsScreen
          offererId={String(offererId)}
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
