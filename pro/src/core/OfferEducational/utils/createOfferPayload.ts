import {
  OfferAddressType,
  PostCollectiveOfferTemplateBodyModel,
} from 'apiClient/v1'

import { IOfferEducationalFormValues } from '../types'

import { parseDuration } from './parseDuration'
import { serializeParticipants } from './serializeParticipants'

const disabilityCompliances = (
  accessibility: IOfferEducationalFormValues['accessibility']
): Pick<
  PostCollectiveOfferTemplateBodyModel,
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

export const createCollectiveOfferPayload = (
  offer: IOfferEducationalFormValues,
  isTemplate: boolean,
  offerTemplateId?: number
): PostCollectiveOfferTemplateBodyModel => ({
  venueId: Number(offer.venueId),
  subcategoryId: offer.subCategory,
  name: offer.title,
  bookingEmails: offer.notificationEmails,
  description: offer.description,
  durationMinutes: parseDuration(offer.duration),
  ...disabilityCompliances(offer.accessibility),
  students: serializeParticipants(offer.participants),
  offerVenue: {
    ...offer.eventAddress,
    venueId: Number(offer.eventAddress.venueId),
  },
  contactEmail: offer.email,
  contactPhone: offer.phone,
  domains: offer.domains.map(domainIdString => Number(domainIdString)),
  interventionArea:
    offer.eventAddress.addressType === OfferAddressType.OFFERER_VENUE
      ? []
      : offer.interventionArea,
  templateId: offerTemplateId,
  priceDetail: isTemplate ? offer.priceDetail : undefined,
})
