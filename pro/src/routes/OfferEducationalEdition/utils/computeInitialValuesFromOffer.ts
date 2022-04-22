import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  PARTICIPANTS,
  CollectiveOffer,
} from 'core/OfferEducational'
import { Offer } from 'custom_types/offer'

const computeDurationString = (
  durationMinutes: number | undefined | null
): string => {
  if (!durationMinutes) return DEFAULT_EAC_FORM_VALUES.duration
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  return `${hours > 9 ? hours : `0${hours}`}:${
    minutes > 9 ? minutes : `0${minutes}`
  }`
}

const offerIsCollectiveOffer = (
  offer: Offer | CollectiveOffer
): offer is CollectiveOffer => 'students' in offer

export const computeInitialValuesFromOffer = (
  offer: Offer | CollectiveOffer,
  category: string,
  subCategory: string
): Omit<IOfferEducationalFormValues, 'offererId' | 'venueId'> => {
  const eventAddress = offerIsCollectiveOffer(offer)
    ? offer?.offerVenue
    : offer?.extraData?.offerVenue

  const participants = offerIsCollectiveOffer(offer)
    ? {
        quatrieme: offer.students.includes(PARTICIPANTS.quatrieme),
        troisieme: offer.students.includes(PARTICIPANTS.troisieme),
        CAPAnnee1: offer.students.includes(PARTICIPANTS.CAPAnnee1),
        CAPAnnee2: offer.students.includes(PARTICIPANTS.CAPAnnee2),
        seconde: offer.students.includes(PARTICIPANTS.seconde),
        premiere: offer.students.includes(PARTICIPANTS.premiere),
        terminale: offer.students.includes(PARTICIPANTS.terminale),
      }
    : offer?.extraData?.students && {
        quatrieme: offer.extraData.students.includes(PARTICIPANTS.quatrieme),
        troisieme: offer.extraData.students.includes(PARTICIPANTS.troisieme),
        CAPAnnee1: offer.extraData.students.includes(PARTICIPANTS.CAPAnnee1),
        CAPAnnee2: offer.extraData.students.includes(PARTICIPANTS.CAPAnnee2),
        seconde: offer.extraData.students.includes(PARTICIPANTS.seconde),
        premiere: offer.extraData.students.includes(PARTICIPANTS.premiere),
        terminale: offer.extraData.students.includes(PARTICIPANTS.terminale),
      }

  const email = offerIsCollectiveOffer(offer)
    ? offer.contactEmail
    : offer?.extraData?.contactEmail

  const phone = offerIsCollectiveOffer(offer)
    ? offer.contactPhone
    : offer?.extraData?.contactPhone

  return {
    category,
    subCategory,
    title: offer.name,
    description: offer.description ?? DEFAULT_EAC_FORM_VALUES.description,
    duration: computeDurationString(offer.durationMinutes),
    eventAddress: eventAddress || DEFAULT_EAC_FORM_VALUES.eventAddress,
    participants: participants || DEFAULT_EAC_FORM_VALUES.participants,
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
    email: email ?? DEFAULT_EAC_FORM_VALUES.email,
    phone: phone ?? DEFAULT_EAC_FORM_VALUES.phone,
    notifications: !!offer.bookingEmail,
    notificationEmail:
      offer.bookingEmail ?? DEFAULT_EAC_FORM_VALUES.notificationEmail,
  }
}
