import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import type { PriceTableFormContext } from '../../types'
import { toFormValues } from '../toFormValues'

describe('toFormValues', () => {
  const baseOffer = getIndividualOfferFactory({ id: 123 })

  const makeContext = (offer = baseOffer): PriceTableFormContext => ({
    isCaledonian: false,
    mode: OFFER_WIZARD_MODE.CREATION,
    offer,
  })

  it('should map existing price categories (event offer)', () => {
    const offer = { ...baseOffer, isEvent: true }
    const context = makeContext(offer)
    const priceCategories = [
      {
        id: 1,
        label: 'Plein tarif',
        price: 20,
        offerId: offer.id,
        bookingsQuantity: 2,
        quantity: 10,
        remainingQuantity: null,
        activationCodes: [],
        activationCodesExpirationDatetime: '',
      },
    ]

    const result = toFormValues(offer, priceCategories, context)

    expect(result.entries).toHaveLength(1)
    expect(result.entries[0].label).toBe('Plein tarif')
    expect(result.entries[0].offerId).toBe(offer.id)
  })

  it('should create a default entry with label for empty event offer', () => {
    const offer = { ...baseOffer, isEvent: true }
    const context = makeContext(offer)

    const result = toFormValues(offer, [], context)

    expect(result.entries).toHaveLength(1)
    expect(result.entries[0].label).toBe('Tarif unique')
    expect(result.entries[0].offerId).toBe(offer.id)
  })

  it('should create a default entry with null label for empty non-event offer', () => {
    const offer = { ...baseOffer, isEvent: false }
    const context = makeContext(offer)

    const result = toFormValues(offer, [], context)

    expect(result.entries).toHaveLength(1)
    expect(result.entries[0].label).toBeNull()
  })
})
