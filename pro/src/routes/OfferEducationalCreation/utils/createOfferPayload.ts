import {
  IOfferEducationalFormValues,
  PARTICIPANTS,
} from 'core/OfferEducational'

type CreateEducationalOfferPayload = {
  offererId: string
  venueId: string
  subcategoryId: string
  name: string
  bookingEmail?: string
  description?: string
  durationMinutes?: number
  audioDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  extraData: Record<string, unknown>
}

const parseDuration = (duration: string): number | undefined => {
  if (!duration) {
    return undefined
  }

  const [hours, minutes] = duration
    .split(':')
    .map(numberString => parseInt(numberString))

  return hours * 60 + minutes
}

const disabilityCompliances = (
  accessibility: IOfferEducationalFormValues['accessibility']
): Pick<
  CreateEducationalOfferPayload,
  | 'audioDisabilityCompliant'
  | 'mentalDisabilityCompliant'
  | 'motorDisabilityCompliant'
  | 'visualDisabilityCompliant'
> => ({
  audioDisabilityCompliant: accessibility.audio,
  mentalDisabilityCompliant: accessibility.mental,
  motorDisabilityCompliant: accessibility.motor,
  visualDisabilityCompliant: accessibility.visual,
})

const getStudents = (
  participants: IOfferEducationalFormValues['participants']
): string[] =>
  Object.keys(participants)
    .filter(
      (key: string): boolean =>
        participants[key as keyof typeof participants] === true
    )
    .map(key => PARTICIPANTS[key])

export const createOfferPayload = (
  offer: IOfferEducationalFormValues
): CreateEducationalOfferPayload => ({
  offererId: offer.offererId,
  venueId: offer.venueId,
  subcategoryId: offer.subCategory,
  name: offer.title,
  bookingEmail: offer.notifications ? offer.notificationEmail : undefined,
  description: offer.description,
  durationMinutes: parseDuration(offer.duration),
  ...disabilityCompliances(offer.accessibility),
  extraData: {
    students: getStudents(offer.participants),
    offerVenue: offer.eventAddress,
    contactEmail: offer.email,
    contactPhone: offer.phone,
  },
})
