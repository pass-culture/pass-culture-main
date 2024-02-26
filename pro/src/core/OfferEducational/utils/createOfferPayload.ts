import {
  DateRangeOnCreateModel,
  OfferAddressType,
  PostCollectiveOfferTemplateBodyModel,
} from 'apiClient/v1'
import { buildDateTime } from 'screens/IndividualOffer/StocksEventEdition/adapters/serializers'
import {
  formatBrowserTimezonedDateAsUTC,
  toISOStringWithoutMilliseconds,
} from 'utils/date'

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
  beginningDatetime: string,
  endingDatetime: string,
  hour?: string
): DateRangeOnCreateModel => {
  const beginningDateTimeInUserTimezone = buildDateTime(
    beginningDatetime,
    hour || '00:00'
  )
  const startDateWithoutTz = new Date(
    formatBrowserTimezonedDateAsUTC(beginningDateTimeInUserTimezone)
  )
  const endDateWithoutTz = new Date(
    formatBrowserTimezonedDateAsUTC(buildDateTime(endingDatetime, '23:59'))
  )
  return {
    start: toISOStringWithoutMilliseconds(startDateWithoutTz),
    end: toISOStringWithoutMilliseconds(endDateWithoutTz),
  }
}

export const createCollectiveOfferPayload = (
  offer: OfferEducationalFormValues,
  isTemplate: boolean,
  offerTemplateId?: number
): PostCollectiveOfferTemplateBodyModel => {
  return {
    venueId: Number(offer.venueId),
    subcategoryId: null,
    name: offer.title,
    bookingEmails: offer.notificationEmails,
    description: offer.description,
    durationMinutes: parseDuration(offer.duration),
    ...disabilityCompliances(offer.accessibility),
    students: serializeParticipants(offer.participants),
    offerVenue: {
      ...offer.eventAddress,
      venueId: Number(offer.eventAddress.venueId),
    },
    contactEmail: offer.email,
    contactPhone: offer.phone,
    domains: offer.domains.map((domainIdString) => Number(domainIdString)),
    interventionArea:
      offer.eventAddress.addressType === OfferAddressType.OFFERER_VENUE
        ? []
        : offer.interventionArea,
    templateId: offerTemplateId,
    priceDetail: isTemplate ? offer.priceDetail : undefined,
    nationalProgramId: Number(offer.nationalProgramId),
    dates:
      isTemplate &&
      offer.datesType === 'specific_dates' &&
      offer.beginningDate &&
      offer.endingDate
        ? serializeDates(offer.beginningDate, offer.endingDate, offer.hour)
        : undefined,
    formats: offer.formats,
  }
}
