import isEqual from 'lodash.isequal'

import {
  EducationalOfferModelPayload,
  IOfferEducationalFormValues,
  parseDuration,
  serializeParticipants,
} from 'core/OfferEducational'

type DeepPartialEducationalOfferModelPayload = Omit<
  Partial<EducationalOfferModelPayload>,
  'extraData'
> & {
  extraData?: Partial<EducationalOfferModelPayload['extraData']>
}

export const createPatchOfferPayload = (
  offer: IOfferEducationalFormValues,
  initialValues: IOfferEducationalFormValues
): DeepPartialEducationalOfferModelPayload => {
  let changedValues: DeepPartialEducationalOfferModelPayload = {}

  const offerKeys = Object.keys(offer) as (keyof IOfferEducationalFormValues)[]

  offerKeys.forEach(key => {
    if (!isEqual(offer[key], initialValues[key])) {
      switch (key) {
        case 'title':
          changedValues.name = offer.title
          break
        case 'description':
          changedValues.description = offer.description
          break
        case 'duration':
          changedValues.durationMinutes = parseDuration(offer.duration)
          break
        case 'eventAddress':
          changedValues = {
            ...changedValues,
            extraData: {
              ...changedValues.extraData,
              offerVenue: offer.eventAddress,
            },
          }
          break
        case 'participants':
          changedValues = {
            ...changedValues,
            extraData: {
              ...changedValues.extraData,
              students: serializeParticipants(offer.participants),
            },
          }
          break
        case 'accessibility':
          changedValues.mentalDisabilityCompliant = offer.accessibility.mental
          changedValues.motorDisabilityCompliant = offer.accessibility.motor
          changedValues.audioDisabilityCompliant = offer.accessibility.audio
          changedValues.visualDisabilityCompliant = offer.accessibility.visual
          break
        case 'phone':
          changedValues = {
            ...changedValues,
            extraData: {
              ...changedValues.extraData,
              contactPhone: offer.phone,
            },
          }
          break
        case 'email':
          changedValues = {
            ...changedValues,
            extraData: {
              ...changedValues.extraData,
              contactEmail: offer.email,
            },
          }
          break
        case 'notificationEmail':
          if (offer.notifications) {
            changedValues.bookingEmail = offer.notificationEmail
          }
          break
        case 'notifications':
          if (offer.notifications === true) {
            changedValues.bookingEmail = offer.notificationEmail
          } else {
            changedValues.bookingEmail = ''
          }
          break
      }
    }
  })

  return changedValues
}
