import isEqual from 'lodash.isequal'

import { OfferContactFormEnum } from 'apiClient/adage'
import {
  PatchCollectiveOfferBodyModel,
  PatchCollectiveOfferTemplateBodyModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'core/OfferEducational/types'
import { serializeDates } from 'core/OfferEducational/utils/createOfferPayload'
import { parseDuration } from 'core/OfferEducational/utils/parseDuration'
import { serializeParticipants } from 'core/OfferEducational/utils/serializeParticipants'

type PatchOfferSerializer<T> = {
  [key in keyof OfferEducationalFormValues]?: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => T
}

const serializer: PatchOfferSerializer<PatchCollectiveOfferBodyModel> = {
  title: (payload, offer) => ({ ...payload, name: offer.title }),
  description: (payload, offer) => ({
    ...payload,
    description: offer.description,
  }),
  duration: (payload, offer) => ({
    ...payload,
    durationMinutes: parseDuration(offer.duration),
  }),
  accessibility: (payload, offer) => ({
    ...payload,
    mentalDisabilityCompliant: offer.accessibility.mental,
    motorDisabilityCompliant: offer.accessibility.motor,
    audioDisabilityCompliant: offer.accessibility.audio,
    visualDisabilityCompliant: offer.accessibility.visual,
  }),
  notificationEmails: (payload, offer) => {
    return {
      ...payload,
      bookingEmails: offer.notificationEmails,
    }
  },
  offererId: (payload: PatchCollectiveOfferBodyModel) => payload,
  venueId: (payload, offer) => ({
    ...payload,
    venueId: Number(offer.venueId),
  }),
  eventAddress: (payload, offer) => {
    const eventAddressPayload = {
      ...offer.eventAddress,
      venueId: offer.eventAddress.venueId,
    }
    return {
      ...payload,
      offerVenue: eventAddressPayload,
    }
  },
  participants: (payload, offer) => ({
    ...payload,
    students: serializeParticipants(offer.participants),
  }),
  phone: (payload, offer) => ({
    ...payload,
    contactPhone: offer.phone,
  }),
  email: (payload, offer) => ({
    ...payload,
    contactEmail: offer.email,
  }),
  domains: (payload, offer) => ({
    ...payload,
    domains: offer.domains.map((domainIdString) => Number(domainIdString)),
  }),
  interventionArea: (payload, offer) => ({
    ...payload,
    interventionArea: offer.interventionArea,
  }),
  nationalProgramId: (payload, offer) => ({
    ...payload,
    nationalProgramId: offer.nationalProgramId
      ? Number(offer.nationalProgramId)
      : null,
  }),
  formats: (payload, offer) => ({
    ...payload,
    formats: offer.formats,
  }),
}

const templateSerializer: PatchOfferSerializer<PatchCollectiveOfferTemplateBodyModel> =
  {
    ...serializer,
    priceDetail: (payload, offer) => ({
      ...payload,
      priceDetail: offer.priceDetail,
    }),
  }

export const createPatchOfferPayload = (
  offer: OfferEducationalFormValues,
  initialValues: OfferEducationalFormValues
): PatchCollectiveOfferBodyModel => {
  let changedValues: PatchCollectiveOfferBodyModel = {}

  const offerKeys = Object.keys(offer) as (keyof OfferEducationalFormValues)[]

  const keysToOmmit = ['imageUrl', 'imageCredit', 'isTemplate']
  offerKeys.forEach((key) => {
    if (
      !isEqual(offer[key], initialValues[key]) &&
      !key.startsWith('search-') &&
      !keysToOmmit.includes(key)
    ) {
      changedValues = serializer[key]?.(changedValues, offer) ?? {}
    }
  })
  // We use this to patch field when user want to make it empty
  changedValues.contactPhone = offer.phone || null
  changedValues.nationalProgramId = Number(offer.nationalProgramId) || null

  return changedValues
}

export const createPatchOfferTemplatePayload = (
  offer: OfferEducationalFormValues,
  initialValues: OfferEducationalFormValues
): PatchCollectiveOfferTemplateBodyModel => {
  const keysToOmmit: (keyof OfferEducationalFormValues)[] = [
    'imageUrl',
    'imageCredit',
    'beginningDate',
    'endingDate',
    'datesType',
    'hour',
    'isTemplate',
    'contactFormType',
    'contactOptions',
  ]
  let changedValues: PatchCollectiveOfferTemplateBodyModel = {}

  const offerKeys = Object.keys(offer) as (keyof OfferEducationalFormValues)[]

  offerKeys.forEach((key) => {
    if (
      !keysToOmmit.includes(key) &&
      !isEqual(offer[key], initialValues[key]) &&
      !key.startsWith('search-')
    ) {
      changedValues = templateSerializer[key]?.(changedValues, offer) ?? {}
    }
  })

  changedValues.contactEmail =
    (offer.contactOptions?.email && offer.email) || null
  changedValues.contactPhone =
    (offer.contactOptions?.phone && offer.phone) || null
  changedValues.contactForm =
    offer.contactOptions?.form && offer.contactFormType === 'form'
      ? OfferContactFormEnum.FORM
      : null
  changedValues.contactUrl =
    offer.contactOptions?.form && offer.contactFormType === 'url'
      ? offer.contactUrl
      : null

  changedValues.nationalProgramId = Number(offer.nationalProgramId) || null
  changedValues.dates =
    offer.datesType === 'specific_dates' &&
    offer.beginningDate &&
    offer.endingDate
      ? serializeDates(offer.beginningDate, offer.endingDate, offer.hour)
      : null
  return changedValues
}
