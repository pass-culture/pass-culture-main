import {
  CategoryResponseModel,
  GetMusicTypesResponse,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { IndividualOffer } from 'core/Offers/types'

const serializerOfferSubCategoryFields = (
  offer: IndividualOffer,
  subCategory?: SubcategoryResponseModel,
  musicTypes?: GetMusicTypesResponse
): {
  author: string
  stageDirector: string
  musicTypeName: string
  gtl_id?: string
  showTypeName: string
  showSubTypeName: string
  speaker: string
  visa: string
  performer: string
  ean: string
  durationMinutes: string
} => {
  if (subCategory === undefined) {
    return {
      author: '',
      stageDirector: '',
      musicTypeName: '',
      gtl_id: '',
      showTypeName: '',
      showSubTypeName: '',
      speaker: '',
      visa: '',
      performer: '',
      ean: '',
      durationMinutes: '',
    }
  }

  const gtl_id = offer.gtl_id
  const musicType = musicTypes?.find((item) => item.gtl_id === gtl_id)?.label
  const showType = showOptionsTree.find(
    (item) => item.code === parseInt(offer.showType, 10)
  )
  const showSubType = showType?.children.find(
    (item) => item.code === parseInt(offer.showSubType, 10)
  )

  const defaultValue = (fieldName: string) =>
    subCategory.conditionalFields.includes(fieldName) ? ' - ' : ''
  return {
    author: offer.author || defaultValue('author'),
    stageDirector: offer.stageDirector || defaultValue('stageDirector'),
    musicTypeName: musicType ?? defaultValue('musicType'),
    gtl_id: gtl_id,
    showTypeName: showType?.label || defaultValue('showType'),
    showSubTypeName: showSubType?.label || defaultValue('showSubType'),
    speaker: offer.speaker || defaultValue('speaker'),
    visa: offer.visa || defaultValue('visa'),
    performer: offer.performer || defaultValue('performer'),
    ean: offer.ean || defaultValue('ean'),
    durationMinutes:
      offer.durationMinutes?.toString() || defaultValue('durationMinutes'),
  }
}

export type OfferSectionData = ReturnType<typeof serializeOfferSectionData>

export const serializeOfferSectionData = (
  offer: IndividualOffer,
  categories: CategoryResponseModel[],
  subCategories: SubcategoryResponseModel[],
  musicTypes?: GetMusicTypesResponse
) => {
  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )
  const offerCategory = categories.find(
    (c) => c.id === offerSubCategory?.categoryId
  )
  const baseOffer = {
    id: offer.id,
    name: offer.name,
    description: offer.description,
    categoryName: offerCategory?.proLabel || ' - ',
    subCategoryName: offerSubCategory?.proLabel || ' - ',
    subcategoryId: offer.subcategoryId,

    venueName: offer.venue.name,
    venuePublicName: offer.venue.publicName,
    venueDepartmentCode: offer.venue.departementCode,
    isVenueVirtual: offer.venue.isVirtual,
    offererName: offer.venue.managingOfferer.name,
    bookingEmail: offer.bookingEmail,
    bookingContact: offer.bookingContact,
    withdrawalDetails: offer.withdrawalDetails || '',
    withdrawalType: offer.withdrawalType || null,
    withdrawalDelay: offer.withdrawalDelay || null,
    accessibility: offer.accessibility,
    status: offer.status,

    isDuo: offer.isDuo,
    url: offer.url,
    externalTicketOfficeUrl: offer.externalTicketOfficeUrl,
  }
  const subCategoryData = serializerOfferSubCategoryFields(
    offer,
    offerSubCategory,
    musicTypes
  )
  return {
    ...baseOffer,
    ...subCategoryData,
  }
}
