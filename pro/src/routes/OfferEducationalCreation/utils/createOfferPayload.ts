import { IOfferEducationalFormValues } from "core/OfferEducational"

type CreateEducationalOfferPayload = {
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

export const createOfferPayload = (
  offer: IOfferEducationalFormValues
): CreateEducationalOfferPayload => ({
  venueId: offer.venueId,
  subcategoryId: offer.subCategory,
  name: offer.title,
  bookingEmail: offer.notifications ? offer.notificationEmail : undefined,
  description: offer.description,
  durationMinutes: offer.duration || undefined,
  audioDisabilityCompliant: offer.audioDisabilityCompliant,
  mentalDisabilityCompliant: offer.mentalDisabilityCompliant,
  motorDisabilityCompliant: offer.motorDisabilityCompliant,
  visualDisabilityCompliant: offer.visualDisabilityCompliant,
  extraData: {
    students: offer.participants,
    offerVenue: offer.eventAddress,
    contactEmail: offer.email,
    contactPhone: offer.phone,
  },
})
