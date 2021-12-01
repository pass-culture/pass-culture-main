import {
  IOfferEducationalFormValues,
  ACCESSIBILITY,
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

  return hours / 60 + minutes
}

const disabilityCompliances = (
  accessibility: string[]
): Pick<
  CreateEducationalOfferPayload,
  | 'audioDisabilityCompliant'
  | 'mentalDisabilityCompliant'
  | 'motorDisabilityCompliant'
  | 'visualDisabilityCompliant'
> => ({
  audioDisabilityCompliant: accessibility.includes(ACCESSIBILITY.AUDIO),
  mentalDisabilityCompliant: accessibility.includes(ACCESSIBILITY.MENTAL),
  motorDisabilityCompliant: accessibility.includes(ACCESSIBILITY.MOTOR),
  visualDisabilityCompliant: accessibility.includes(ACCESSIBILITY.VISUAL),
})

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
    students: offer.participants,
    offerVenue: offer.eventAddress,
    contactEmail: offer.email,
    contactPhone: offer.phone,
  },
})
