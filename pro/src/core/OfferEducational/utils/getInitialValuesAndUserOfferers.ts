import {
  GetEducationalOffererResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'

import { DEFAULT_EAC_FORM_VALUES } from '../constants'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  EducationalCategories,
} from '../types'

import { computeInitialValuesFromOffer } from './computeInitialValuesFromOffer'

interface GetInitialValuesAndUserOfferersParams {
  categories: EducationalCategories
  offerers: GetEducationalOffererResponseModel[]
  offer: CollectiveOffer | CollectiveOfferTemplate
}

export const getInitialValuesAndUserOfferers = ({
  categories,
  offerers,
  offer,
}: GetInitialValuesAndUserOfferersParams) => {
  const offerSubcategory = categories.educationalSubCategories.find(
    ({ id }) => offer.subcategoryId === id
  )

  const offerCategory = offerSubcategory
    ? categories.educationalCategories.find(
        ({ id }) => offerSubcategory.categoryId === id
      )
    : undefined

  const userOfferers = offerers.filter(offerer =>
    offerer.managedVenues.map(venue => venue.id).includes(offer.venueId)
  )

  const initialValuesFromOffer = computeInitialValuesFromOffer(
    offer,
    offerCategory?.id ?? '',
    (offerSubcategory?.id ??
      DEFAULT_EAC_FORM_VALUES.subCategory) as SubcategoryIdEnum
  )

  return {
    userOfferers,
    initialValues: initialValuesFromOffer,
  }
}
