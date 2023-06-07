import {
  musicOptionsTree,
  showOptionsTree,
} from 'core/Offers/categoriesSubTypes'
import {
  IOfferIndividual,
  IOfferSubCategory,
  IOfferCategory,
} from 'core/Offers/types'

const serializerOfferSubCategoryFields = (
  offer: IOfferIndividual,
  subCategory?: IOfferSubCategory
): {
  author: string
  stageDirector: string
  musicTypeName: string
  musicSubTypeName: string
  showTypeName: string
  showSubTypeName: string
  speaker: string
  visa: string
  performer: string
  isbn: string
  durationMinutes: string
} => {
  if (subCategory === undefined) {
    return {
      author: '',
      stageDirector: '',
      musicTypeName: '',
      musicSubTypeName: '',
      showTypeName: '',
      showSubTypeName: '',
      speaker: '',
      visa: '',
      performer: '',
      isbn: '',
      durationMinutes: '',
    }
  }

  const musicType = musicOptionsTree.find(
    item => item.code === parseInt(offer.musicType, 10)
  )
  const musicSubType = musicType?.children.find(
    item => item.code === parseInt(offer.musicSubType, 10)
  )
  const showType = showOptionsTree.find(
    item => item.code === parseInt(offer.showType, 10)
  )
  const showSubType = showType?.children.find(
    item => item.code === parseInt(offer.showSubType, 10)
  )

  const defaultValue = (fieldName: string) =>
    subCategory.conditionalFields.includes(fieldName) ? ' - ' : ''
  return {
    author: offer.author || defaultValue('author'),
    stageDirector: offer.stageDirector || defaultValue('stageDirector'),
    musicTypeName: musicType?.label || defaultValue('musicType'),
    musicSubTypeName: musicSubType?.label || defaultValue('musicSubType'),
    showTypeName: showType?.label || defaultValue('showType'),
    showSubTypeName: showSubType?.label || defaultValue('showSubType'),
    speaker: offer.speaker || defaultValue('speaker'),
    visa: offer.visa || defaultValue('visa'),
    performer: offer.performer || defaultValue('performer'),
    isbn: offer.isbn || defaultValue('isbn'),
    durationMinutes:
      offer.durationMinutes?.toString() || defaultValue('durationMinutes'),
  }
}

export const serializeOfferSectionData = (
  offer: IOfferIndividual,
  categories: IOfferCategory[],
  subCategories: IOfferSubCategory[]
) => {
  const offerSubCategory = subCategories.find(s => s.id === offer.subcategoryId)
  const offerCategory = categories.find(
    c => c.id === offerSubCategory?.categoryId
  )
  const baseOffer = {
    nonHumanizedId: offer.nonHumanizedId,
    name: offer.name,
    description: offer.description,
    categoryName: offerCategory?.proLabel || ' - ',
    subCategoryName: offerSubCategory?.proLabel || ' - ',
    subcategoryId: offer.subcategoryId,

    venueName: offer.venue.name,
    venuePublicName: offer.venue.publicName,
    venueDepartmentCode: offer.venue.departmentCode,
    isVenueVirtual: offer.venue.isVirtual,
    offererName: offer.venue.offerer.name,
    bookingEmail: offer.bookingEmail,
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
    offerSubCategory
  )
  return {
    ...baseOffer,
    ...subCategoryData,
  }
}
