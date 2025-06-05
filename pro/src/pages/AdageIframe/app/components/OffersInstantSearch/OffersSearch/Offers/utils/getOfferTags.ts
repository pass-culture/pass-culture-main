import {
  AuthenticatedResponse,
  CollectiveLocationType,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  OfferAddressType,
} from 'apiClient/adage'
import {
  getHumanizeRelativeDistance,
  humanizeDistance,
} from 'commons/utils/getDistance'
import fullLocationIcon from 'icons/full-location.svg'
import fullProfileIcon from 'icons/full-profil.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import strokeBagIcon from 'icons/stroke-bag.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import {
  getFormattedDatesForBookableOffer,
  getFormattedDatesForTemplateOffer,
} from 'pages/AdageIframe/app/components/OfferInfos/AdageOffer/utils/adageOfferDates'
import { isCollectiveOfferTemplate } from 'pages/AdageIframe/app/types'

type OfferTag = {
  icon?: string
  text: string
}

function getFormattedPrice(price: number) {
  return price > 0
    ? new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR',
      }).format(price / 100)
    : 'Gratuit'
}

export function getOfferTags(
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel,
  adageUser: AuthenticatedResponse,
  showAllTags: boolean = true,
  isCollectiveOaActive: boolean = false
) {
  const isTemplate = isCollectiveOfferTemplate(offer)

  const distanceToOfferer =
    offer.venue.coordinates.latitude &&
    offer.venue.coordinates.longitude &&
    (adageUser.lat || adageUser.lat === 0) &&
    (adageUser.lon || adageUser.lon === 0) &&
    getHumanizeRelativeDistance(
      {
        latitude: offer.venue.coordinates.latitude,
        longitude: offer.venue.coordinates.longitude,
      },
      {
        latitude: adageUser.lat,
        longitude: adageUser.lon,
      }
    )

  const distanceFromOffer =
    offer.location &&
    offer.location.address &&
    offer.location.address.latitude &&
    offer.location.address.longitude &&
    (adageUser.lat || adageUser.lat === 0) &&
    (adageUser.lon || adageUser.lon === 0) &&
    getHumanizeRelativeDistance(
      {
        latitude: offer.location.address.latitude,
        longitude: offer.location.address.longitude,
      },
      {
        latitude: adageUser.lat,
        longitude: adageUser.lon,
      }
    )

  const tags: OfferTag[] = []
  if (isCollectiveOaActive && offer.location) {
    const locationTypeMap = {
      [CollectiveLocationType.SCHOOL]: {
        icon: fullLocationIcon,
        text: 'Dans l’établissement scolaire',
      },
      [CollectiveLocationType.ADDRESS]: {
        icon: fullLocationIcon,
        text: `Sortie à ${distanceFromOffer}`,
      },
      [CollectiveLocationType.TO_BE_DEFINED]: {
        icon: fullLocationIcon,
        text: 'Lieu à déterminer',
      },
    }

    const locationTag = locationTypeMap[offer.location.locationType]
    tags.push(locationTag)

    if (distanceToOfferer && showAllTags) {
      tags.push({
        icon: fullLocationIcon,
        text: `Partenaire situé à ${distanceToOfferer}`,
      })
    }
  } else {
    const locationTypeMap = {
      [OfferAddressType.SCHOOL]: {
        icon: fullLocationIcon,
        text: 'Dans l’établissement scolaire',
      },
      [OfferAddressType.OFFERER_VENUE]: {
        icon: fullLocationIcon,
        text: 'Sortie',
      },
      [OfferAddressType.OTHER]: [
        { icon: fullLocationIcon, text: 'Sortie' },
        { icon: fullLocationIcon, text: 'Lieu à définir' },
      ],
    }

    const locationTag = locationTypeMap[offer.offerVenue.addressType]
    tags.push(...(Array.isArray(locationTag) ? locationTag : [locationTag]))

    if (OfferAddressType.OFFERER_VENUE === offer.offerVenue.addressType && offer.offerVenue.distance || offer.offerVenue.distance === 0) {
      tags.push({
        icon: fullLocationIcon,
        text: `À ${humanizeDistance(offer.offerVenue.distance * 1000)}`,
      })
    }

    if (
      OfferAddressType.SCHOOL === offer.offerVenue.addressType ||
      OfferAddressType.OTHER === offer.offerVenue.addressType
    ) {
      if (distanceToOfferer && showAllTags) {
        tags.push({
          icon: fullLocationIcon,
          text: `Partenaire situé à ${distanceToOfferer}`,
        })
      }
    }
  }

  if (!showAllTags) {
    return tags
  }

  if (isTemplate) {
    tags.push({
      icon: fullWaitIcon,
      text: `${getFormattedDatesForTemplateOffer(offer, 'Disponible toute l’année')}`,
    })
  } else if (offer.stock.startDatetime) {
    tags.push({
      icon: fullWaitIcon,
      text: `${getFormattedDatesForBookableOffer(offer)}`,
    })
  }

  if (offer.students.length > 0) {
    tags.push({
      icon: strokeBagIcon,
      text: `${offer.students.length > 1 ? 'Multiniveaux' : offer.students[0]}`,
    })
  }

  if (!isTemplate) {
    tags.push({
      icon: strokeEuroIcon,
      text: `${getFormattedPrice(offer.stock.price)}`,
    })
    tags.push({
      icon: fullProfileIcon,
      text: `${offer.stock.numberOfTickets} élèves`,
    })
  }

  return tags
}
