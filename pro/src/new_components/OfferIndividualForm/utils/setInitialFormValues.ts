import { IOfferIndividual, IOfferSubCategory } from 'core/Offers/types'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'

const setInitialFormValues = (
  offer: IOfferIndividual,
  subCategoryList: IOfferSubCategory[]
): IOfferIndividualFormValues => {
  const subCategory = subCategoryList.find(
    (s: IOfferSubCategory) => s.id === offer.subcategoryId
  )

  if (subCategory === undefined) {
    throw Error("La categorie de l'offre est introuvable")
  }

  // TODO add computed subcategory fields on merge of:
  // https://github.com/pass-culture/pass-culture-main/pull/3126
  const subCategoryFields: string[] = [...subCategory.conditionalFields]

  return {
    isEvent: subCategory.isEvent || false,
    subCategoryFields: subCategoryFields,
    name: offer.name,
    description: offer.description,
    offererId: offer.offererId,
    venueId: offer.venueId,
    isNational: offer.isNational,
    categoryId: subCategory.categoryId,
    subcategoryId: offer.subcategoryId,
    showType: offer.showType,
    showSubType: offer.showSubType,
    musicType: offer.musicType,
    musicSubType: offer.musicSubType,
    withdrawalDetails:
      offer.withdrawalDetails || FORM_DEFAULT_VALUES['withdrawalDetails'],
    withdrawalDelay: offer.withdrawalDelay,
    withdrawalType: offer.withdrawalType,
    accessibility: offer.accessibility,
  }
}

export default setInitialFormValues
