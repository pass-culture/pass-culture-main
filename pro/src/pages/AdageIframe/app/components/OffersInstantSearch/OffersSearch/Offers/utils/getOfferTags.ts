import {
  type AuthenticatedResponse,
  CollectiveLocationType,
  type CollectiveOfferResponseModel,
  type CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import { getHumanizeRelativeDistance } from '@/commons/utils/getDistance'
import fullLocationIcon from '@/icons/full-location.svg'
import fullProfileIcon from '@/icons/full-profil.svg'
import fullWaitIcon from '@/icons/full-wait.svg'
import strokeBagIcon from '@/icons/stroke-bag.svg'
import strokeEuroIcon from '@/icons/stroke-euro.svg'
import {
  getFormattedDatesForBookableOffer,
  getFormattedDatesForTemplateOffer,
} from '@/pages/AdageIframe/app/components/OfferInfos/AdageOffer/utils/adageOfferDates'
import { isCollectiveOfferTemplate } from '@/pages/AdageIframe/app/types'

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
  showAllTags: boolean = true
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
    offer.location?.location?.latitude &&
    offer.location.location.longitude &&
    (adageUser.lat || adageUser.lat === 0) &&
    (adageUser.lon || adageUser.lon === 0) &&
    getHumanizeRelativeDistance(
      {
        latitude: offer.location.location.latitude,
        longitude: offer.location.location.longitude,
      },
      {
        latitude: adageUser.lat,
        longitude: adageUser.lon,
      }
    )

  const tags: OfferTag[] = []
  if (offer.location) {
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
