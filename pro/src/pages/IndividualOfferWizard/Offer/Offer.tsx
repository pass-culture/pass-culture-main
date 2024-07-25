import { useSelector } from 'react-redux'
import { useSearchParams } from 'react-router-dom'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { BannerCreateOfferAdmin } from 'components/Banner/BannerCreateOfferAdmin'
import {
  GET_VENUES_QUERY_KEY,
  GET_OFFERER_NAMES_QUERY_KEY,
} from 'config/swrQueryKeys'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import { IndivualOfferLayout } from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import { InformationsScreen } from 'screens/IndividualOffer/InformationsScreen/InformationsScreen'
import { selectCurrentOffererId } from 'store/user/selectors'
import { Spinner } from 'ui-kit/Spinner/Spinner'

export const Offer = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { currentUser } = useCurrentUser()
  const { offer } = useIndividualOfferContext()
  const [searchParams] = useSearchParams()

  let venueId = searchParams.get('lieu')

  const offererIdFromQueryParam = searchParams.get('structure')
    ? Number(searchParams.get('structure'))
    : undefined
  const selectedOffererId = useSelector(selectCurrentOffererId)

  // At first we look for the offerer id in the offer,
  // then in the query params
  // after all we look for the selected offerer id in the redux store
  const offererId =
    offer?.venue.managingOfferer.id ??
    offererIdFromQueryParam ??
    selectedOffererId

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
