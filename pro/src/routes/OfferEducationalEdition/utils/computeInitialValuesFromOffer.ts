import {
  GetCollectiveOfferTemplateResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import {
  CollectiveOffer,
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  PARTICIPANTS,
} from 'core/OfferEducational'

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

export const computeInitialValuesFromOffer = (
  offer: CollectiveOffer | GetCollectiveOfferTemplateResponseModel,
  category: string,
  subCategory: SubcategoryIdEnum
): Omit<IOfferEducationalFormValues, 'offererId' | 'venueId'> => {
  const eventAddress = offer?.offerVenue

  const participants = {
    quatrieme: offer.students.includes(PARTICIPANTS.quatrieme),
    troisieme: offer.students.includes(PARTICIPANTS.troisieme),
    CAPAnnee1: offer.students.includes(PARTICIPANTS.CAPAnnee1),
    CAPAnnee2: offer.students.includes(PARTICIPANTS.CAPAnnee2),
    seconde: offer.students.includes(PARTICIPANTS.seconde),
    premiere: offer.students.includes(PARTICIPANTS.premiere),
    terminale: offer.students.includes(PARTICIPANTS.terminale),
  }

  const email = offer.contactEmail

  const phone = offer.contactPhone

  const domains = offer.domains.map(({ id }) => id.toString())

  return {
    category,
    subCategory,
    title: offer.name,
    description: offer.description ?? DEFAULT_EAC_FORM_VALUES.description,
    duration: computeDurationString(offer.durationMinutes),
    eventAddress: eventAddress || DEFAULT_EAC_FORM_VALUES.eventAddress,
    participants: participants || DEFAULT_EAC_FORM_VALUES.participants,
    accessibility: {
      audio: Boolean(offer.audioDisabilityCompliant),
      mental: Boolean(offer.mentalDisabilityCompliant),
      motor: Boolean(offer.motorDisabilityCompliant),
      visual: Boolean(offer.visualDisabilityCompliant),
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
    domains,
    // FIXME : set offer.interventionArea when backend is ready
    interventionArea: DEFAULT_EAC_FORM_VALUES.interventionArea,
  }
}
