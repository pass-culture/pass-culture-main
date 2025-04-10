import { OfferContactFormEnum } from 'apiClient/adage'
import {
  DateRangeOnCreateModel,
  PatchCollectiveOfferBodyModel,
  PatchCollectiveOfferTemplateBodyModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { serializeDates } from 'commons/core/OfferEducational/utils/createOfferPayload'
import { parseDuration } from 'commons/core/OfferEducational/utils/parseDuration'
import { serializeParticipants } from 'commons/core/OfferEducational/utils/serializeParticipants'
import { isEqual } from 'commons/utils/isEqual'

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
  location: (payload, offer) => ({
    ...payload,
    location: offer.location,
  }),
  participants: (payload, offer) => ({
    ...payload,
    students: serializeParticipants(offer.participants),
  }),
  phone: (payload, offer) => ({
    ...payload,
    contactPhone: offer.phone || null,
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
  initialValues: OfferEducationalFormValues,
  isCollectiveOaActive: boolean
): PatchCollectiveOfferBodyModel => {
  let changedValues: PatchCollectiveOfferBodyModel = {}

  const offerKeys = Object.keys(offer) as (keyof OfferEducationalFormValues)[]

  const keysToOmit = ['imageUrl', 'imageCredit', 'isTemplate']
  isCollectiveOaActive
    ? keysToOmit.push('eventAddress')
    : keysToOmit.push('location')

  offerKeys.forEach((key) => {
    if (
      !isEqual(offer[key], initialValues[key]) &&
      !key.startsWith('search-') &&
      !keysToOmit.includes(key)
    ) {
      changedValues = serializer[key]?.(changedValues, offer) ?? {}
    }
  })

  return changedValues
}

export const createPatchOfferTemplatePayload = (
  offer: OfferEducationalFormValues,
  initialValues: OfferEducationalFormValues,
  isCollectiveOaActive: boolean
): PatchCollectiveOfferTemplateBodyModel => {
  const keysToOmit: (keyof OfferEducationalFormValues)[] = [
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

  isCollectiveOaActive
    ? keysToOmit.push('eventAddress')
    : keysToOmit.push('location')
  let changedValues: PatchCollectiveOfferTemplateBodyModel = {}

  const offerKeys = Object.keys(offer) as (keyof OfferEducationalFormValues)[]

  offerKeys.forEach((key) => {
    if (
      !keysToOmit.includes(key) &&
      !isEqual(offer[key], initialValues[key]) &&
      !key.startsWith('search-')
    ) {
      changedValues = templateSerializer[key]?.(changedValues, offer) ?? {}
    }
  })

  const newContactEmail = getEmail(offer)
  const initialContactMail = getEmail(initialValues)
  if (!isEqual(newContactEmail, initialContactMail)) {
    changedValues.contactEmail = newContactEmail
  }

  const newContactPhone = getPhone(offer)
  const initialContactPhone = getPhone(initialValues)
  if (!isEqual(newContactPhone, initialContactPhone)) {
    changedValues.contactPhone = newContactPhone
  }

  const newContactForm = getForm(offer)
  const initialContactForm = getForm(initialValues)
  if (!isEqual(newContactForm, initialContactForm)) {
    changedValues.contactForm = newContactForm
  }

  const newContactUrl = getUrl(offer)
  const initialContactUrl = getUrl(initialValues)
  if (!isEqual(newContactUrl, initialContactUrl)) {
    changedValues.contactUrl = newContactUrl
  }

  const newDates = getDates(offer)
  const initialDates = getDates(initialValues)
  if (!isEqual(newDates, initialDates)) {
    changedValues.dates = newDates
  }

  return changedValues
}

 const getEmail = (offer: OfferEducationalFormValues): string | null => {
  return (offer.contactOptions?.email && offer.email) || null
 }

 const getPhone = (offer: OfferEducationalFormValues): string | null => {
  return (offer.contactOptions?.phone && offer.phone) || null
 }

 const getForm = (offer: OfferEducationalFormValues): OfferContactFormEnum | null => {
  return offer.contactOptions?.form && offer.contactFormType === 'form' ? OfferContactFormEnum.FORM : null
 }

 const getUrl = (offer: OfferEducationalFormValues): string | null | undefined => {
  return offer.contactOptions?.form && offer.contactFormType === 'url' ? offer.contactUrl : null
 }

 const getDates = (offer: OfferEducationalFormValues): DateRangeOnCreateModel | null => {
  return offer.datesType === 'specific_dates' &&
  offer.beginningDate &&
  offer.endingDate
    ? serializeDates(offer.beginningDate, offer.endingDate, offer.hour)
    : null
 }
