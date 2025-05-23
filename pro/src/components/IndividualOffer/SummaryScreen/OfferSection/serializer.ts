import {
  CategoryResponseModel,
  GetIndividualOfferResponseModel,
  type GetIndividualOfferWithAddressResponseModel,
  GetMusicTypesResponse,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import { showOptionsTree } from 'commons/core/Offers/categoriesSubTypes'

const getMusicData = (
  offer: GetIndividualOfferResponseModel,
  musicTypes?: GetMusicTypesResponse,
  gtl_id?: string
): {
  musicTypeName?: string
  musicSubTypeName?: string
  gtl_id?: string
} => {
  return {
    musicTypeName:
      (musicTypes ?? []).length === 0
        ? undefined
        : musicTypes?.find(
            (item) => item.gtl_id.substring(0, 2) === gtl_id?.substring(0, 2) // Gtl_id is a string of 8 characters, only first 2 are relevant to music genre
          )?.label,
    gtl_id: offer.extraData?.gtl_id,
  }
}

const serializerOfferSubCategoryFields = (
  offer: GetIndividualOfferResponseModel,
  subCategory?: SubcategoryResponseModel,
  musicTypes?: GetMusicTypesResponse
): {
  author: string
  stageDirector: string
  musicTypeName: string
  musicSubTypeName: string
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
      musicSubTypeName: '',
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
  const showType = showOptionsTree.find(
    (item) => item.code === parseInt(offer.extraData?.showType, 10)
  )
  const showSubType = showType?.children.find(
    (item) => item.code === parseInt(offer.extraData?.showSubType, 10)
  )

  const { musicTypeName, musicSubTypeName, gtl_id } = getMusicData(
    offer,
    musicTypes,
    offer.extraData?.gtl_id
  )

  const defaultValue = (fieldName: string) =>
    subCategory.conditionalFields.includes(fieldName) ? ' - ' : ''
  return {
    author: offer.extraData?.author || defaultValue('author'),
    stageDirector:
      offer.extraData?.stageDirector || defaultValue('stageDirector'),
    musicTypeName: musicTypeName || defaultValue('musicType'),
    musicSubTypeName: musicSubTypeName || defaultValue('musicSubType'),
    gtl_id: gtl_id,
    showTypeName: showType?.label || defaultValue('showType'),
    showSubTypeName: showSubType?.label || defaultValue('showSubType'),
    speaker: offer.extraData?.speaker || defaultValue('speaker'),
    visa: offer.extraData?.visa || defaultValue('visa'),
    performer: offer.extraData?.performer || defaultValue('performer'),
    ean: offer.extraData?.ean || defaultValue('ean'),
    durationMinutes:
      offer.durationMinutes?.toString() || defaultValue('durationMinutes'),
  }
}

export const serializeOfferSectionData = (
  offer: GetIndividualOfferWithAddressResponseModel,
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
    offererName: offer.venue.managingOfferer.name,
    bookingEmail: offer.bookingEmail,
    bookingContact: offer.bookingContact,
    withdrawalDetails: offer.withdrawalDetails || '',
    withdrawalType: offer.withdrawalType || null,
    withdrawalDelay: offer.withdrawalDelay || null,
    status: offer.status,
    isProductBased: !!offer.productId,
    isDuo: offer.isDuo,
    url: offer.url,
  }
  const subCategoryData = serializerOfferSubCategoryFields(
    offer,
    offerSubCategory,
    musicTypes
  )

  let offerAddressData

  // Could be simpler with lodash.pick
  if (offer.address) {
    offerAddressData = {
      address: {
        label: offer.address.label,
        city: offer.address.city,
        street: offer.address.street,
        postalCode: offer.address.postalCode,
      },
    }
  }

  return {
    ...baseOffer,
    ...subCategoryData,
    ...offerAddressData,
  }
}
