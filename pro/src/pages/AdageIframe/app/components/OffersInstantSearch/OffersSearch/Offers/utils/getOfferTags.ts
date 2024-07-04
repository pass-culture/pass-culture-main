import {
  AuthenticatedResponse,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import {
  getFormattedDatesForBookableOffer,
  getFormattedDatesForTemplateOffer,
} from 'pages/AdageIframe/app/components/OfferInfos/AdageOffer/utils/adageOfferDates'
import { isCollectiveOfferTemplate } from 'pages/AdageIframe/app/types'
import {
  getHumanizeRelativeDistance,
  humanizeDistance,
} from 'utils/getDistance'

type OfferTag = {
  icon: string
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

  const tags: OfferTag[] = []
  switch (offer.offerVenue.addressType) {
    case OfferAddressType.SCHOOL: {
      tags.push({ icon: '📚', text: 'Dans l’établissement scolaire' })
      if (distanceToOfferer && showAllTags) {
        tags.push({
          icon: '👩‍🎨',
          text: `Partenaire situé à ${distanceToOfferer}`,
        })
      }
      break
    }
    case OfferAddressType.OFFERER_VENUE: {
      tags.push({ icon: '🎒', text: 'Sortie' })
      if (offer.offerVenue.distance || offer.offerVenue.distance === 0) {
        tags.push({
          icon: '📍',
          text: `À ${humanizeDistance(offer.offerVenue.distance * 1000)}`,
        })
      }
      break
    }
    case OfferAddressType.OTHER: {
      tags.push(
        { icon: '🎒', text: 'Sortie' },
        { icon: '📍', text: 'Lieu à définir' }
      )

      if (distanceToOfferer && showAllTags) {
        tags.push({
          icon: '👩‍🎨',
          text: `Partenaire situé à ${distanceToOfferer}`,
        })
      }
      break
    }
    default:
  }

  if (!showAllTags) {
    return tags
  }

  if (isTemplate) {
    tags.push({
      icon: '🕐',
      text: `${getFormattedDatesForTemplateOffer(offer, 'Disponible toute l’année')}`,
    })
  } else if (offer.stock.startDatetime) {
    tags.push({
      icon: '🕐',
      text: `${getFormattedDatesForBookableOffer(offer)}`,
    })
  }

  if (offer.students.length > 0) {
    tags.push({
      icon: '🧑‍🏫',
      text: `${offer.students.length > 1 ? 'Multiniveaux' : offer.students[0]}`,
    })
  }

  if (!isTemplate) {
    tags.push({ icon: '💰', text: `${getFormattedPrice(offer.stock.price)}` })

    tags.push({ icon: '🧑‍🎓', text: `${offer.stock.numberOfTickets} élèves` })
  }

  return tags
}
