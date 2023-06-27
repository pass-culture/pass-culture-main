import isEqual from 'lodash.isequal'

import { PatchCollectiveOfferBodyModel } from 'apiClient/v1'
import {
  OfferEducationalFormValues,
  parseDuration,
  serializeParticipants,
} from 'core/OfferEducational'

const serializer = {
  title: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({ ...payload, name: offer.title }),
  description: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({ ...payload, description: offer.description }),
  duration: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({ ...payload, durationMinutes: parseDuration(offer.duration) }),
  subCategory: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({ ...payload, subcategoryId: offer.subCategory }),
  accessibility: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({
    ...payload,
    mentalDisabilityCompliant: offer.accessibility.mental,
    motorDisabilityCompliant: offer.accessibility.motor,
    audioDisabilityCompliant: offer.accessibility.audio,
    visualDisabilityCompliant: offer.accessibility.visual,
  }),
  notificationEmails: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => {
    return {
      ...payload,
      bookingEmails: offer.notificationEmails,
    }
  },
  notifications: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => {
    return {
      ...payload,
      bookingEmails: offer.notificationEmails,
    }
  },
  // Unchanged keys
  // Need to put them here for ts not to raise an error
  offererId: (payload: PatchCollectiveOfferBodyModel) => payload,
  venueId: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({
    ...payload,
    venueId: offer.venueId,
  }),
  category: (payload: PatchCollectiveOfferBodyModel) => payload,
  eventAddress: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => {
    const eventAddressPayload = {
      ...offer.eventAddress,
      venueId: offer.eventAddress.venueId,
    }
    return {
      ...payload,
      offerVenue: eventAddressPayload,
    }
  },
  participants: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({
    ...payload,
    students: serializeParticipants(offer.participants),
  }),
  phone: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({
    ...payload,
    contactPhone: offer.phone,
  }),
  email: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({
    ...payload,
    contactEmail: offer.email,
  }),
  domains: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({
    ...payload,
    domains: offer.domains.map(domainIdString => Number(domainIdString)),
  }),
  interventionArea: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({
    ...payload,
    interventionArea: offer.interventionArea,
  }),
}

const templateSerializer = {
  ...serializer,
  venueId: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({
    ...payload,
    venueId: offer.venueId,
  }),
  priceDetail: (
    payload: PatchCollectiveOfferBodyModel,
    offer: OfferEducationalFormValues
  ) => ({
    ...payload,
    priceDetail: offer.priceDetail,
  }),
}

export const createPatchOfferPayload = (
  offer: OfferEducationalFormValues,
  initialValues: OfferEducationalFormValues,
  isTemplate: boolean
): PatchCollectiveOfferBodyModel => {
  let changedValues: PatchCollectiveOfferBodyModel = {}

  const offerKeys = Object.keys(offer) as (keyof OfferEducationalFormValues)[]

  const offerSerializer = isTemplate ? templateSerializer : serializer

  offerKeys.forEach(key => {
    if (
      !isEqual(offer[key], initialValues[key]) &&
      !key.startsWith('search-') &&
      key !== 'imageUrl' &&
      key !== 'imageCredit'
    ) {
      // This is because startsWith eliminates the two keys that are not defined in the collectiveOfferSerializer
      // @ts-expect-error (7053) Element implicitly has an 'any' type because expression of type 'keyof IOfferEducationalFormValues' can't be used to index type

      changedValues = offerSerializer[key](changedValues, offer)
    }
  })
  // We use this to patch phone number when user want to make it empty
  changedValues.contactPhone = offer.phone || null
  return changedValues
}
