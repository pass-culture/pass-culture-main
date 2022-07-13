import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import {
  IOfferSectionProps,
  IStockEventItemProps,
  IStockThingSectionProps,
} from 'screens/OfferIndividual/Summary'
import {
  musicOptionsTree,
  showOptionsTree,
} from 'core/Offers/categoriesSubTypes'

import { IOfferAppPreviewProps } from 'new_components/OfferAppPreview'
import { IOfferIndividual } from 'core/Offers/types'

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

const serializerOfferSectionProps = (
  offer: IOfferIndividual,
  categories: IOfferCategory[],
  subCategories: IOfferSubCategory[]
): IOfferSectionProps => {
  const offerSubCategory = subCategories.find(s => s.id === offer.subcategoryId)
  const offerCategory = categories.find(
    c => c.id === offerSubCategory?.categoryId
  )
  const baseOffer = {
    id: offer.id,
    nonHumanizedId: offer.nonHumanizedId,
    name: offer.name,
    description: offer.description,
    categoryName: offerCategory?.proLabel || ' - ',
    subCategoryName: offerSubCategory?.proLabel || ' - ',
    subcategoryId: offer.subcategoryId,

    venueName: offer.venue.name,
    venuePublicName: offer.venue.publicName,
    isVenueVirtual: offer.venue.isVirtual,
    offererName: offer.venue.offerer.name,
    bookingEmail: offer.bookingEmail,
    withdrawalDetails: offer.withdrawalDetails || '',
    withdrawalType: offer.withdrawalType || null,
    withdrawalDelay: offer.withdrawalDelay || null,

    visualDisabilityCompliant: offer.visualDisabilityCompliant || false,
    mentalDisabilityCompliant: offer.mentalDisabilityCompliant || false,
    motorDisabilityCompliant: offer.motorDisabilityCompliant || false,
    audioDisabilityCompliant: offer.audioDisabilityCompliant || false,
    noDisabilityCompliant: offer.noDisabilityCompliant || false,

    isDuo: offer.isDuo,
    url: offer.externalTicketOfficeUrl,
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

const serializerStockThingSectionProps = (
  offer: IOfferIndividual
): IStockThingSectionProps | undefined => {
  if (offer.isEvent || offer.stocks.length === 0) {
    return undefined
  }

  const stock = offer.stocks[0]
  return {
    quantity: stock.quantity,
    price: stock.price,
    bookingLimitDatetime: stock.bookingLimitDatetime,
  }
}

const serializerStockEventSectionProps = (
  offer: IOfferIndividual
): IStockEventItemProps[] | undefined => {
  if (!offer.isEvent || offer.stocks.length === 0) {
    return undefined
  }
  return offer.stocks.map(stock => ({
    quantity: stock.quantity,
    price: stock.price,
    bookingLimitDatetime: stock.bookingLimitDatetime,
    beginningDateTime: stock.beginningDatetime,
  }))
}

const serializerPreviewProps = (
  offer: IOfferIndividual
): IOfferAppPreviewProps => {
  return {
    imageSrc: offer.thumbUrl,
    offerData: {
      name: offer.name,
      description: offer.description,
      isEvent: offer.isEvent,
      isDuo: offer.isDuo,
    },
    venueData: {
      isVirtual: offer.venue.isVirtual,
      name: offer.venue.name,
      publicName: offer.venue.publicName,
      address: offer.venue.address,
      postalCode: offer.venue.postalCode,
      city: offer.venue.city,
      withdrawalDetails: offer.withdrawalDetails || '',
    },
  }
}

export const serializePropsFromOfferIndividual = (
  offer: IOfferIndividual,
  categories: IOfferCategory[],
  subCategories: IOfferSubCategory[]
): {
  offer: IOfferSectionProps
  stockThing?: IStockThingSectionProps
  stockEventList?: IStockEventItemProps[]
  preview: IOfferAppPreviewProps
} => {
  return {
    offer: serializerOfferSectionProps(offer, categories, subCategories),
    stockThing: serializerStockThingSectionProps(offer),
    stockEventList: serializerStockEventSectionProps(offer),
    preview: serializerPreviewProps(offer),
  }
}
