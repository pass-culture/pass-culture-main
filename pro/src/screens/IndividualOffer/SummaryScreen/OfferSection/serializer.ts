import {
  CategoryResponseModel,
  GetIndividualOfferResponseModel,
  GetMusicTypesResponse,
  SubcategoryResponseModel,
} from 'apiClient/v1'
import {
  musicOptionsTree,
  showOptionsTree,
} from 'core/Offers/categoriesSubTypes'

const getMusicData = (
  isTiteliveMusicGenreEnabled: boolean,
  offer: GetIndividualOfferResponseModel,
  musicTypes?: GetMusicTypesResponse,
  gtl_id?: string
): {
  musicTypeName?: string
  musicSubTypeName?: string
  gtl_id?: string
} => {
  if (isTiteliveMusicGenreEnabled) {
    return {
      musicTypeName: musicTypes?.find(
        (item) => item.gtl_id.substring(0, 2) === gtl_id?.substring(0, 2) // Gtl_id is a string of 8 characters, only first 2 are relevant to music genre
      )?.label,
      gtl_id: offer.extraData?.gtl_id,
    }
  }

  const offerMusicType = offer.extraData?.musicType
  const offerMusicSubType = offer.extraData?.musicSubType
  if (!offerMusicType || !offerMusicSubType) {
    return {}
  }
  const musicTypeItem = musicOptionsTree.find(
    (item) => item.code === parseInt(offerMusicType, 10)
  )
  const children = musicTypeItem?.children
  if (children === undefined) {
    throw new Error('Music subtype not found')
  }
  return {
    musicTypeName: musicTypeItem?.label,
    musicSubTypeName: children.find(
      (item) => item.code === parseInt(offerMusicSubType, 10)
    )?.label,
  }
}

const serializerOfferSubCategoryFields = (
  offer: GetIndividualOfferResponseModel,
  isTiteliveMusicGenreEnabled: boolean,
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
    isTiteliveMusicGenreEnabled,
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
  offer: GetIndividualOfferResponseModel,
  categories: CategoryResponseModel[],
  subCategories: SubcategoryResponseModel[],
  isTiteliveMusicGenreEnabled: boolean,
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
    status: offer.status,

    isDuo: offer.isDuo,
    url: offer.url,
    externalTicketOfficeUrl: offer.externalTicketOfficeUrl,
  }
  const subCategoryData = serializerOfferSubCategoryFields(
    offer,
    isTiteliveMusicGenreEnabled,
    offerSubCategory,
    musicTypes
  )
  return {
    ...baseOffer,
    ...subCategoryData,
  }
}
