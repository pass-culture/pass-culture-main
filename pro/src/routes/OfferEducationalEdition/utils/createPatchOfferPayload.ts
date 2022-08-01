import isEqual from 'lodash.isequal'

import { PatchCollectiveOfferBodyModel } from 'apiClient/v1'
import {
  IOfferEducationalFormValues,
  parseDuration,
  serializeParticipants,
} from 'core/OfferEducational'

const serializer = {
  title: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, name: offer.title }),
  description: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, description: offer.description }),
  duration: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, durationMinutes: parseDuration(offer.duration) }),
  subCategory: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({ ...payload, subcategoryId: offer.subCategory }),
  accessibility: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    mentalDisabilityCompliant: offer.accessibility.mental,
    motorDisabilityCompliant: offer.accessibility.motor,
    audioDisabilityCompliant: offer.accessibility.audio,
    visualDisabilityCompliant: offer.accessibility.visual,
  }),
  notificationEmail: (
    payload: PatchCollectiveOfferBodyModel,
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
    payload: PatchCollectiveOfferBodyModel,
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
  offererId: (payload: PatchCollectiveOfferBodyModel) => payload,
  venueId: (payload: PatchCollectiveOfferBodyModel) => payload,
  category: (payload: PatchCollectiveOfferBodyModel) => payload,
  domains: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    domains: offer.domains,
  }),
}

const collectiveOfferSerializer = {
  ...serializer,
  eventAddress: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    offerVenue: offer.eventAddress,
  }),
  participants: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    students: serializeParticipants(offer.participants),
  }),
  phone: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    contactPhone: offer.phone,
  }),
  email: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    contactEmail: offer.email,
  }),
  domains: (
    payload: PatchCollectiveOfferBodyModel,
    offer: IOfferEducationalFormValues
  ) => ({
    ...payload,
    domains: offer.domains.map(domainIdString => Number(domainIdString)),
  }),
  // FIXME: send interventionArea when backend is ready
  interventionArea: (payload: PatchCollectiveOfferBodyModel) => payload,
}

export const createPatchOfferPayload = (
  offer: IOfferEducationalFormValues,
  initialValues: IOfferEducationalFormValues
): PatchCollectiveOfferBodyModel => {
  let changedValues: PatchCollectiveOfferBodyModel = {}

  const offerKeys = Object.keys(offer) as (keyof IOfferEducationalFormValues)[]

  offerKeys.forEach(key => {
    if (!isEqual(offer[key], initialValues[key]) && key !== 'search-domains') {
      changedValues = collectiveOfferSerializer[key](changedValues, offer)
    }
  })

  return changedValues
}
