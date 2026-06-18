import {
  ArtistType,
  type CategoryResponseModel,
  type GetIndividualOfferWithAddressResponseModel,
  type GetMusicTypesResponse,
  type SubcategoryResponseModel,
} from '@/apiClient/v1'
import { showOptionsTree } from '@/commons/core/Offers/categoriesSubTypes'
import type { OfferExtraData } from '@/commons/core/Offers/types'
import { isOfferProductBased } from '@/commons/core/Offers/utils/typology'

function stringifyArtist(
  artistOfferLinks: GetIndividualOfferWithAddressResponseModel['artistOfferLinks'],
  filter: ArtistType
) {
  if (artistOfferLinks.length < 1) {
    return
  }

  return artistOfferLinks
    .filter((a) => a.artistType === filter)
    .map((a) => a.artistName)
    .join(', ')
}

export function serializeArtist(
  offer: GetIndividualOfferWithAddressResponseModel,
  artistExtraData: string | undefined,
  defaultValue: string,
  artistType: ArtistType
) {
  const isProductBased = isOfferProductBased(offer)

  if (isProductBased) {
    return artistExtraData ?? defaultValue
  } else {
    return stringifyArtist(offer.artistOfferLinks, artistType) ?? defaultValue
  }
}

const getMusicData = (
  offer: GetIndividualOfferWithAddressResponseModel,
  musicTypes?: GetMusicTypesResponse,
  gtl_id?: string
): {
  musicTypeName?: string
  musicSubTypeName?: string
  gtl_id?: string
} => {
  const extraData = offer.extraData as OfferExtraData | undefined

  return {
    musicTypeName:
      (musicTypes ?? []).length === 0
        ? undefined
        : musicTypes?.find(
            (item) => item.gtl_id.substring(0, 2) === gtl_id?.substring(0, 2) // Gtl_id is a string of 8 characters, only first 2 are relevant to music genre
          )?.label,
    gtl_id: extraData?.gtl_id,
  }
}

const serializerOfferSubCategoryFields = (
  offer: GetIndividualOfferWithAddressResponseModel,
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
  const extraData = offer.extraData as OfferExtraData | undefined

  const showType = showOptionsTree.find(
    (item) => item.code === Number.parseInt(extraData?.showType ?? '', 10)
  )
  const showSubType = showType?.children.find(
    (item) => item.code === Number.parseInt(extraData?.showSubType ?? '', 10)
  )

  const { musicTypeName, musicSubTypeName, gtl_id } = getMusicData(
    offer,
    musicTypes,
    extraData?.gtl_id
  )

  const defaultValue = (fieldName: string) =>
    subCategory.conditionalFields.includes(fieldName) ? ' - ' : ''
  return {
    author: serializeArtist(
      offer,
      extraData?.author,
      defaultValue('author'),
      ArtistType.AUTHOR
    ),
    stageDirector: serializeArtist(
      offer,
      extraData?.stageDirector,
      defaultValue('stageDirector'),
      ArtistType.STAGE_DIRECTOR
    ),
    musicTypeName: musicTypeName || defaultValue('musicType'),
    musicSubTypeName: musicSubTypeName || defaultValue('musicSubType'),
    gtl_id: gtl_id,
    showTypeName: showType?.label || defaultValue('showType'),
    showSubTypeName: showSubType?.label || defaultValue('showSubType'),
    speaker: extraData?.speaker || defaultValue('speaker'),
    visa: extraData?.visa || defaultValue('visa'),
    performer: serializeArtist(
      offer,
      extraData?.performer,
      defaultValue('performer'),
      ArtistType.PERFORMER
    ),
    ean: extraData?.ean || defaultValue('ean'),
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
    artistOfferLinks: offer.artistOfferLinks,
  }
  const subCategoryData = serializerOfferSubCategoryFields(
    offer,
    offerSubCategory,
    musicTypes
  )

  let offerAddressData:
    | {
        location?: {
          label?: string | null
          city: string
          street?: string | null
          postalCode: string
        }
      }
    | undefined

  // Could be simpler with lodash.pick
  if (offer.location) {
    offerAddressData = {
      location: {
        label: offer.location.label,
        city: offer.location.city,
        street: offer.location.street,
        postalCode: offer.location.postalCode,
      },
    }
  }

  return {
    ...baseOffer,
    ...subCategoryData,
    ...offerAddressData,
  }
}
