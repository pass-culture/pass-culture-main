import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'

const setInitialFormValues = (
  values: IOfferIndividualFormValues,
  offererNames: TOffererName[],
  offererId: string | null,
  venueId: string | null,
  venueList: TOfferIndividualVenue[]
): IOfferIndividualFormValues => {
  let initialOffererId = FORM_DEFAULT_VALUES.offererId
  if (offererNames.length === 1) {
    initialOffererId = offererNames[0]
      .id as IOfferIndividualFormValues['offererId']
  } else if (
    offererId &&
    offererNames.find(offerer => offerer.id === offererId)
  ) {
    initialOffererId = offererId
  }

  let initialVenueId = FORM_DEFAULT_VALUES.venueId
  let initialWithdrawalDetails = FORM_DEFAULT_VALUES.withdrawalDetails
  let initialAccessibility = FORM_DEFAULT_VALUES.accessibility
  if (initialOffererId !== FORM_DEFAULT_VALUES.offererId) {
    const offererVenues = venueList.filter(
      (venue: TOfferIndividualVenue) =>
        venue.managingOffererId === initialOffererId
    )
    if (offererVenues.length === 1) {
      initialVenueId = offererVenues[0].id
    }
  }
  const venue = venueList.find(venue => venue.id === venueId)
  if (venueId && venue) {
    initialVenueId = venueId
    initialAccessibility = venue.accessibility

    if (venue.withdrawalDetails) {
      initialWithdrawalDetails = venue.withdrawalDetails
    }
  }

  return {
    ...values,
    offererId: initialOffererId,
    venueId: initialVenueId,
    withdrawalDetails: initialWithdrawalDetails,
    accessibility: initialAccessibility,
  }
}

export default setInitialFormValues
