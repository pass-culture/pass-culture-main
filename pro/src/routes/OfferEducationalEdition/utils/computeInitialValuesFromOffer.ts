import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  PARTICIPANTS,
} from 'core/OfferEducational'
import { Offer } from 'custom_types/offer'

const computeDurationString = (durationMinutes: number | undefined) => {
  if (!durationMinutes) return DEFAULT_EAC_FORM_VALUES.duration
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  return `${hours > 9 ? hours : `0${hours}`}:${
    minutes > 9 ? minutes : `0${minutes}`
  }`
}

export const computeInitialValuesFromOffer = (
  offer: Offer,
  category: string,
  subCategory: string
): Omit<IOfferEducationalFormValues, 'offererId' | 'venueId'> => {
  return {
    category,
    subCategory,
    title: offer.name,
    description: offer.description ?? DEFAULT_EAC_FORM_VALUES.description,
    duration: computeDurationString(offer.durationMinutes),
    eventAddress:
      offer?.extraData?.offerVenue || DEFAULT_EAC_FORM_VALUES.eventAddress,
    participants: offer?.extraData?.students
      ? {
          quatrieme: offer.extraData.students.includes(PARTICIPANTS.quatrieme),
          troisieme: offer.extraData.students.includes(PARTICIPANTS.troisieme),
          CAPAnnee1: offer.extraData.students.includes(PARTICIPANTS.CAPAnnee1),
          CAPAnnee2: offer.extraData.students.includes(PARTICIPANTS.CAPAnnee2),
          seconde: offer.extraData.students.includes(PARTICIPANTS.seconde),
          premiere: offer.extraData.students.includes(PARTICIPANTS.premiere),
          terminale: offer.extraData.students.includes(PARTICIPANTS.terminale),
        }
      : DEFAULT_EAC_FORM_VALUES.participants,
    accessibility: {
      audio: offer.audioDisabilityCompliant,
      mental: offer.mentalDisabilityCompliant,
      motor: offer.motorDisabilityCompliant,
      visual: offer.visualDisabilityCompliant,
      none:
        !offer.audioDisabilityCompliant &&
        !offer.mentalDisabilityCompliant &&
        !offer.motorDisabilityCompliant &&
        !offer.visualDisabilityCompliant,
    },
    email: offer?.extraData?.contactEmail ?? DEFAULT_EAC_FORM_VALUES.email,
    phone: offer?.extraData?.contactPhone ?? DEFAULT_EAC_FORM_VALUES.phone,
    notifications: !!offer.bookingEmail,
    notificationEmail:
      offer.bookingEmail ?? DEFAULT_EAC_FORM_VALUES.notificationEmail,
  }
}
