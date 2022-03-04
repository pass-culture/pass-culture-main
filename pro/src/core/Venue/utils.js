import { stringify } from 'query-string'

export const venueCreateOfferLink = (offererId, venueId, isVirtual) =>
  [
    '/offre/creation',
    stringify({
      structure: offererId,
      lieu: venueId,
      numerique: isVirtual ? null : undefined,
    }),
  ].join('?')
