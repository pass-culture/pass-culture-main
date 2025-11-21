import {
  CollectiveLocationType,
  type DateRangeOnCreateModel,
  OfferContactFormEnum,
  type PostCollectiveOfferBodyModel,
  type PostCollectiveOfferTemplateBodyModel,
} from '@/apiClient/v1'
import {
  buildDateTime,
  formatBrowserTimezonedDateAsUTC,
  toISOStringWithoutMilliseconds,
} from '@/commons/utils/date'

import type { OfferEducationalFormValues } from '../types'
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
  offer: OfferEducationalFormValues
): PostCollectiveOfferBodyModel | PostCollectiveOfferTemplateBodyModel => {
  const getLocationPayload = () => {
    if (offer.location?.locationType === CollectiveLocationType.ADDRESS) {
      const location = offer.location.location?.isVenueLocation
        ? { isVenueLocation: true }
        : {
            ...offer.location.location,
            banId: offer.banId,
            street: offer.street ?? '',
            postalCode: offer.postalCode ?? '',
            latitude: offer.latitude ?? '',
            longitude: offer.longitude ?? '',
            city: offer.city ?? '',
            coords: offer.coords ?? '',
          }

      return {
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          location,
        },
      }
    }

    if (offer.location?.locationType === CollectiveLocationType.TO_BE_DEFINED) {
      return {
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,
          locationComment: offer.location.locationComment || null,
        },
      }
    }

    return {
      location: { locationType: CollectiveLocationType.SCHOOL },
    }
  }

  const getInterventionArea = () => {
    return offer.location?.locationType !== CollectiveLocationType.ADDRESS
      ? offer.interventionArea
      : []
  }

  return {
    venueId: Number(offer.venueId),
    name: offer.title,
    bookingEmails: offer.notificationEmails?.map((email) => email.email) ?? [
      '',
    ],
    description: offer.description,
    durationMinutes: offer.duration ? parseDuration(offer.duration) : undefined,
    ...disabilityCompliances(offer.accessibility),
    students: serializeParticipants(offer.participants),
    ...getLocationPayload(),
    domains: (offer.domains || []).map((domainIdString) =>
      Number(domainIdString)
    ),
    interventionArea: getInterventionArea(),
    nationalProgramId: offer.nationalProgramId
      ? Number(offer.nationalProgramId)
      : null,
    formats: offer.formats,
  } as PostCollectiveOfferBodyModel | PostCollectiveOfferTemplateBodyModel
}

export const createCollectiveOfferTemplatePayload = (
  offer: OfferEducationalFormValues
): PostCollectiveOfferTemplateBodyModel => {
  return {
    ...getCommonOfferPayload(offer),
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
  offerTemplateId?: number
): PostCollectiveOfferBodyModel => {
  return {
    ...getCommonOfferPayload(offer),
    templateId: offerTemplateId,
    contactEmail: offer.email,
    contactPhone: offer.phone,
  }
}
