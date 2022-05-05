import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'
import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'

const setInitialFormValues = (
  values: IOfferIndividualFormValues,
  offererNames: TOffererName[],
  offererId: string | null,
  venueId: string | null,
  venueList: TOfferIndividualVenue[]
): IOfferIndividualFormValues => {
  const setOffererId = () => {
    if (offererNames.length === 1) {
      return offererNames[0].id
    }
    if (offererId && offererNames.find(offerer => offerer.id === offererId)) {
      return offererId
    }
    return FORM_DEFAULT_VALUES.offererId
  }

  const setVenueId = (formOffererId: string) => {
    if (formOffererId) {
      const offererVenues = venueList.filter(
        (venue: TOfferIndividualVenue) =>
          venue.managingOffererId === formOffererId
      )
      if (offererVenues.length === 1) {
        return offererVenues[0].id
      }
    }
    if (venueId && venueList.find(venue => venue.id === venueId)) {
      return venueId
    }
    return FORM_DEFAULT_VALUES.venueId
  }

  const formOffererId = setOffererId()
  return {
    ...values,
    offererId: formOffererId,
    venueId: setVenueId(formOffererId),
  }
}

export default setInitialFormValues
