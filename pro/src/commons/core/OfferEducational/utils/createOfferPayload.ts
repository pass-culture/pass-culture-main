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
  offerFormValues: OfferEducationalFormValues,
  isCollectiveOaActive: boolean
): PostCollectiveOfferBodyModel | PostCollectiveOfferTemplateBodyModel {
  // remove id_oa key from location object as it useful only on a form matter
  delete offerFormValues.location.id_oa

  return {
    venueId: Number(offerFormValues.venueId),
    subcategoryId: null,
    name: offerFormValues.title,
    bookingEmails: offerFormValues.notificationEmails,
    description: offerFormValues.description,
    durationMinutes: parseDuration(offerFormValues.duration),
    ...disabilityCompliances(offerFormValues.accessibility),
    students: serializeParticipants(offerFormValues.participants),
    ...(isCollectiveOaActive
      ? { location: offerFormValues.location }
      : {
          offerVenue: {
            ...offerFormValues.eventAddress,
            venueId: Number(offerFormValues.eventAddress.venueId),
          },
        }),
    domains: offerFormValues.domains.map((domainIdString) =>
      Number(domainIdString)
    ),
    interventionArea:
      offerFormValues.eventAddress.addressType ===
      OfferAddressType.OFFERER_VENUE
        ? []
        : offerFormValues.interventionArea,
    nationalProgramId: Number(offerFormValues.nationalProgramId),
    formats: offerFormValues.formats,
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
