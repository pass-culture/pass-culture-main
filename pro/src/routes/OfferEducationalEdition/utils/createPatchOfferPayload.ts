import {
  EditEducationalOfferPayload,
  IOfferEducationalFormValues,
  parseDuration,
  serializeParticipants,
} from 'core/OfferEducational'

import isEqual from 'lodash.isequal'

const serializer = {
  title: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, name: offer.title }),
  description: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, description: offer.description }),
  duration: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, durationMinutes: parseDuration(offer.duration) }),
  subCategory: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, subcategoryId: offer.subCategory }),
  eventAddress: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    extraData: { ...payload.extraData, offerVenue: offer.eventAddress },
  }),
  participants: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    extraData: {
      ...payload.extraData,
      students: serializeParticipants(offer.participants),
    },
  }),
  accessibility: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    mentalDisabilityCompliant: offer.accessibility.mental,
    motorDisabilityCompliant: offer.accessibility.motor,
    audioDisabilityCompliant: offer.accessibility.audio,
    visualDisabilityCompliant: offer.accessibility.visual,
  }),
  phone: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    extraData: {
      ...payload.extraData,
      contactPhone: offer.phone,
    },
  }),
  email: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    extraData: {
      ...payload.extraData,
      contactEmail: offer.email,
    },
  }),
  notificationEmail: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => {
    if (offer.notifications) {
      return {
        ...payload,
        bookingEmail: offer.notificationEmail,
      }
    }
    return payload
  },
  notifications: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => {
    if (offer.notifications) {
      return {
        ...payload,
        bookingEmail: offer.notificationEmail,
      }
    }
    return {
      ...payload,
      bookingEmail: '',
    }
  },
  // Unchanged keys
  // Need to put them here for ts not to raise an error
  offererId: (payload: EditEducationalOfferPayload) => payload,
  venueId: (payload: EditEducationalOfferPayload) => payload,
  category: (payload: EditEducationalOfferPayload) => payload,
  domains: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    domains: offer.domains,
  }),
}

const collectiveOfferSerializer = {
  ...serializer,
  eventAddress: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    offerVenue: offer.eventAddress,
  }),
  participants: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    students: serializeParticipants(offer.participants),
  }),
  phone: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    contactPhone: offer.phone,
  }),
  email: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    contactEmail: offer.email,
  }),
  domains: (
    payload: EditEducationalOfferPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    domains: offer.domains.map(domainIdString => Number(domainIdString)),
  }),
}

export const createPatchOfferPayload = (
  offer: IOfferEducationalFormValues,
  initialValues: IOfferEducationalFormValues,
  useCollectiveSerializer = false
): EditEducationalOfferPayload => {
  let changedValues: EditEducationalOfferPayload = {}

  const offerKeys = Object.keys(offer) as (keyof IOfferEducationalFormValues)[]

  offerKeys.forEach(key => {
    if (!isEqual(offer[key], initialValues[key]) && key !== 'search-domains') {
      changedValues = (
        useCollectiveSerializer ? collectiveOfferSerializer : serializer
      )[key](changedValues, offer)
    }
  })

  return changedValues
}
