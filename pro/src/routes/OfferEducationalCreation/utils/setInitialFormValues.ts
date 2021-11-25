import {
  IEducationalCategory,
  IEducationalSubCategory,
  INITIAL_EDUCATIONAL_FORM_VALUES,
  IOfferEducationalFormValues,
  IUserOfferer,
} from 'core/OfferEducational'

const setInitialFormValues = (
  values: IOfferEducationalFormValues,
  offerers: IUserOfferer[],
  structure: string | null,
  lieu: string | null,
  categories: {
    educationalCategories: IEducationalCategory[]
    educationalSubCategories: IEducationalSubCategory[]
  }
): IOfferEducationalFormValues => {
  const setOffererId = () => {
    if (offerers.length === 1) {
      return offerers[0].id as IOfferEducationalFormValues['offererId']
    }

    if (structure) {
      return structure as IOfferEducationalFormValues['offererId']
    }

    return INITIAL_EDUCATIONAL_FORM_VALUES.offererId
  }

  const setVenueId = () => {
    if (offerers.length === 1 && offerers[0].managedVenues.length === 1) {
      return offerers[0].managedVenues[0]
        .id as IOfferEducationalFormValues['venueId']
    }

    if (structure) {
      const currentOfferer = offerers.find(offerer => offerer.id === structure)

      if (currentOfferer?.managedVenues.length === 1) {
        return currentOfferer.managedVenues[0]
          .id as IOfferEducationalFormValues['venueId']
      }
    }

    if (lieu) {
      return lieu as IOfferEducationalFormValues['venueId']
    }

    return INITIAL_EDUCATIONAL_FORM_VALUES.venueId
  }

  return {
    ...values,
    offererId: setOffererId(),
    venueId: setVenueId(),
  }
}

export default setInitialFormValues
