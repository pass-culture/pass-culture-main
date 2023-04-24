import {
  OfferAddressType,
  PostCollectiveOfferTemplateBodyModel,
} from 'apiClient/v1'
import { dehumanizeId } from 'utils/dehumanize'

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
  offerTemplateId?: string
): PostCollectiveOfferTemplateBodyModel => ({
  venueId: dehumanizeId(offer.venueId) || 0,
  subcategoryId: offer.subCategory,
  name: offer.title,
  bookingEmails: offer.notificationEmails,
  description: offer.description,
  durationMinutes: parseDuration(offer.duration),
  ...disabilityCompliances(offer.accessibility),
  students: serializeParticipants(offer.participants),
  offerVenue: {
    ...offer.eventAddress,
    // @ts-expect-error api expect number
    venueId: dehumanizeId(offer.eventAddress.venueId) || 0,
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
