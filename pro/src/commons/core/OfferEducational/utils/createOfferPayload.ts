import {
  DateRangeOnCreateModel,
  OfferAddressType,
  PostCollectiveOfferTemplateBodyModel,
  PostCollectiveOfferBodyModel,
  OfferContactFormEnum,
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

function getCommonOfferPayload(
  offer: OfferEducationalFormValues,
  isCollectiveOaActive: boolean
): PostCollectiveOfferBodyModel | PostCollectiveOfferTemplateBodyModel {
  return {
    venueId: Number(offer.venueId),
    subcategoryId: null,
    name: offer.title,
    bookingEmails: offer.notificationEmails,
    description: offer.description,
    durationMinutes: parseDuration(offer.duration),
    ...disabilityCompliances(offer.accessibility),
    students: serializeParticipants(offer.participants),
    ...(isCollectiveOaActive
      ? { location: offer.location }
      : {
          offerVenue: {
            ...offer.eventAddress,
            venueId: Number(offer.eventAddress.venueId),
          },
        }),
    domains: offer.domains.map((domainIdString) => Number(domainIdString)),
    interventionArea:
      offer.eventAddress.addressType === OfferAddressType.OFFERER_VENUE
        ? []
        : offer.interventionArea,
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
