import isEqual from 'lodash.isequal'

import {
  DeepPartialEducationalOfferModelPayload,
  IOfferEducationalFormValues,
  parseDuration,
  serializeParticipants,
} from 'core/OfferEducational'

const serializer = {
  title: (
    payload: DeepPartialEducationalOfferModelPayload,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, name: offer.title }),
  description: (
    payload: DeepPartialEducationalOfferModelPayload,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, description: offer.description }),
  duration: (
    payload: DeepPartialEducationalOfferModelPayload,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, durationMinutes: parseDuration(offer.duration) }),
  subCategory: (
    payload: DeepPartialEducationalOfferModelPayload,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, subcategoryId: offer.subCategory }),
  eventAddress: (
    payload: DeepPartialEducationalOfferModelPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    extraData: { ...payload.extraData, offerVenue: offer.eventAddress },
  }),
  participants: (
    payload: DeepPartialEducationalOfferModelPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    extraData: {
      ...payload.extraData,
      students: serializeParticipants(offer.participants),
    },
  }),
  accessibility: (
    payload: DeepPartialEducationalOfferModelPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    mentalDisabilityCompliant: offer.accessibility.mental,
    motorDisabilityCompliant: offer.accessibility.motor,
    audioDisabilityCompliant: offer.accessibility.audio,
    visualDisabilityCompliant: offer.accessibility.visual,
  }),
  phone: (
    payload: DeepPartialEducationalOfferModelPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    extraData: {
      ...payload.extraData,
      contactPhone: offer.phone,
    },
  }),
  email: (
    payload: DeepPartialEducationalOfferModelPayload,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    extraData: {
      ...payload.extraData,
      contactEmail: offer.email,
    },
  }),
  notificationEmail: (
    payload: DeepPartialEducationalOfferModelPayload,
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
    payload: DeepPartialEducationalOfferModelPayload,
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
  offererId: (payload: DeepPartialEducationalOfferModelPayload) => payload,
  venueId: (payload: DeepPartialEducationalOfferModelPayload) => payload,
  category: (payload: DeepPartialEducationalOfferModelPayload) => payload,
}

export const createPatchOfferPayload = (
  offer: IOfferEducationalFormValues,
  initialValues: IOfferEducationalFormValues
): DeepPartialEducationalOfferModelPayload => {
  let changedValues: DeepPartialEducationalOfferModelPayload = {}

  const offerKeys = Object.keys(offer) as (keyof IOfferEducationalFormValues)[]

  offerKeys.forEach(key => {
    if (!isEqual(offer[key], initialValues[key])) {
      changedValues = serializer[key](changedValues, offer)
    }
  })

  return changedValues
}
