import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  IUserOfferer,
} from 'core/OfferEducational'

const setInitialFormValues = (
  values: IOfferEducationalFormValues,
  offerers: IUserOfferer[],
  offererId: string | null,
  venueId: string | null
): IOfferEducationalFormValues => {
  const setOffererId = () => {
    if (offerers.length === 1) {
      return offerers[0].id as IOfferEducationalFormValues['offererId']
    }

    if (offererId) {
      return offererId as IOfferEducationalFormValues['offererId']
    }

    return DEFAULT_EAC_FORM_VALUES.offererId
  }

  const setVenueId = () => {
    if (offerers.length === 1 && offerers[0].managedVenues.length === 1) {
      return offerers[0].managedVenues[0]
        .id as IOfferEducationalFormValues['venueId']
    }

    if (offererId) {
      const currentOfferer = offerers.find(offerer => offerer.id === offererId)

      if (currentOfferer?.managedVenues.length === 1) {
        return currentOfferer.managedVenues[0]
          .id as IOfferEducationalFormValues['venueId']
      }
    }

    if (venueId) {
      return venueId as IOfferEducationalFormValues['venueId']
    }

    return DEFAULT_EAC_FORM_VALUES.venueId
  }

  return {
    ...values,
    offererId: setOffererId(),
    venueId: setVenueId(),
  }
}

export default setInitialFormValues
