import {
  DateRangeOnCreateModel,
  OfferAddressType,
  PostCollectiveOfferTemplateBodyModel,
  PostCollectiveOfferBodyModel,
  OfferContactFormEnum,
  CollectiveLocationType,
} from 'apiClient/v1'
import {
  formatBrowserTimezonedDateAsUTC,
  toISOStringWithoutMilliseconds,
} from 'commons/utils/date'
import { buildDateTime } from 'components/IndividualOffer/StocksEventEdition/serializers'

import { OfferEducationalFormValues } from '../types'

import { parseDuration } from './parseDuration'
import { serializeParticipants } from './serializeParticipants'

const disabilityCompliances = (
  accessibility: OfferEducationalFormValues['accessibility']
): Pick<
  PostCollectiveOfferTemplateBodyModel,
  | 'audioDisabilityCompliant'
  | 'mentalDisabilityCompliant'
  | 'motorDisabilityCompliant'
  | 'visualDisabilityCompliant'
> => ({
  audioDisabilityCompliant: accessibility.audio,
  mentalDisabilityCompliant: accessibility.mental,
  motorDisabilityCompliant: accessibility.motor,
  visualDisabilityCompliant: accessibility.visual,
})

export const serializeDates = (
  startDatetime: string,
  endingDatetime: string,
  hour?: string
): DateRangeOnCreateModel => {
  const startDatetimeInUserTimezone = buildDateTime(
    startDatetime,
    hour || '00:00'
  )
  const startDateWithoutTz = new Date(
    formatBrowserTimezonedDateAsUTC(startDatetimeInUserTimezone)
  )
  const endDateWithoutTz = new Date(
    formatBrowserTimezonedDateAsUTC(buildDateTime(endingDatetime, '23:59'))
  )
  return {
    start: toISOStringWithoutMilliseconds(startDateWithoutTz),
    end: toISOStringWithoutMilliseconds(endDateWithoutTz),
  }
}

const getCommonOfferPayload = (
  offer: OfferEducationalFormValues,
  isCollectiveOaActive: boolean
): PostCollectiveOfferBodyModel | PostCollectiveOfferTemplateBodyModel => {
  // remove id_oa key from location object as it useful only on a form matter
  delete offer.location.address?.id_oa

  const getLocationPayload = () => {
    if (!isCollectiveOaActive) {
      return {
        offerVenue: {
          ...offer.eventAddress,
          venueId: Number(offer.eventAddress.venueId),
        },
      }
    }

    if (offer.location.locationType === CollectiveLocationType.ADDRESS) {
      return {
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          address: {
            ...offer.location.address,
            banId: offer.banId,
            street: offer.street ?? '',
            postalCode: offer.postalCode ?? '',
            latitude: offer.latitude ?? '',
            longitude: offer.longitude ?? '',
            city: offer.city ?? '',
            coords: offer.coords ?? '',
          },
        },
      }
    }

    if (offer.location.locationType === CollectiveLocationType.TO_BE_DEFINED) {
      return {
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,
          locationComment: offer.location.locationComment,
        },
      }
    }

    return {
      location: { locationType: CollectiveLocationType.SCHOOL },
    }
  }

  const getInterventionArea = () => {
    if (!isCollectiveOaActive) {
      return offer.eventAddress.addressType === OfferAddressType.OFFERER_VENUE
        ? []
        : offer.interventionArea
    }

    return offer.location.locationType !== CollectiveLocationType.ADDRESS
      ? offer.interventionArea
      : []
  }

  return {
    venueId: Number(offer.venueId),
    name: offer.title,
    bookingEmails: offer.notificationEmails ?? [''],
    description: offer.description,
    durationMinutes: parseDuration(offer.duration),
    ...disabilityCompliances(offer.accessibility),
    students: serializeParticipants(offer.participants),
    ...getLocationPayload(),
    domains: offer.domains.map((domainIdString) => Number(domainIdString)),
    interventionArea: getInterventionArea(),
    nationalProgramId: Number(offer.nationalProgramId),
    formats: offer.formats,
  }
}

export const createCollectiveOfferTemplatePayload = (
  offer: OfferEducationalFormValues,
  isCollectiveOaActive: boolean
): PostCollectiveOfferTemplateBodyModel => {
  return {
    ...getCommonOfferPayload(offer, isCollectiveOaActive),
    dates:
      offer.datesType === 'specific_dates' &&
      offer.beginningDate &&
      offer.endingDate
        ? serializeDates(offer.beginningDate, offer.endingDate, offer.hour)
        : undefined,
    priceDetail: offer.priceDetail,
    contactEmail: offer.contactOptions?.email ? offer.email : undefined,
    contactPhone: offer.contactOptions?.phone ? offer.phone : undefined,
    contactForm:
      offer.contactOptions?.form && offer.contactFormType === 'form'
        ? OfferContactFormEnum.FORM
        : undefined,
    contactUrl:
      offer.contactOptions?.form && offer.contactFormType === 'url'
        ? offer.contactUrl
        : undefined,
  }
}

export const createCollectiveOfferPayload = (
  offer: OfferEducationalFormValues,
  isCollectiveOaActive: boolean,
  offerTemplateId?: number
): PostCollectiveOfferBodyModel => {
  return {
    ...getCommonOfferPayload(offer, isCollectiveOaActive),
    templateId: offerTemplateId,
    contactEmail: offer.email,
    contactPhone: offer.phone,
  }
}
