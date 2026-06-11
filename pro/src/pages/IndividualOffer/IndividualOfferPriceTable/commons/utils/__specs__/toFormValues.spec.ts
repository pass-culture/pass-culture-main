import type {
  GetOfferStockResponseModel,
  PriceCategoryResponseModel,
} from '@/apiClient/v1/new'
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

  it('should map existing stocks (non-event offer)', () => {
    const offer = { ...baseOffer, isEvent: false }
    const context = makeContext(offer)
    const stocks: GetOfferStockResponseModel[] = [
      {
        id: 1,
        // @ts-expect-error waiting migration GetOfferStockResponseModel to pydanticV2
        activationCodesExpirationDatetime: null,
        // @ts-expect-error waiting migration GetOfferStockResponseModel to pydanticV2
        beginningDatetime: null,
        // @ts-expect-error waiting migration GetOfferStockResponseModel to pydanticV2
        bookingLimitDatetime: null,
        bookingsQuantity: 2,
        hasActivationCode: false,
        isEventDeletable: true,
        price: 20,
        priceCategoryId: 2,
        quantity: 10,
        remainingQuantity: 'infinity',
      },
    ]

    const result = toFormValues(offer, stocks, context)

    expect(result.priceCategories).toHaveLength(1)
    expect(result.priceCategories[0].label).toBeNull()
    expect(result.priceCategories[0].offerId).toBe(offer.id)
  })

  it('should map existing price categories (event offer)', () => {
    const offer = { ...baseOffer, isEvent: true }
    const context = makeContext(offer)
    const priceCategories: PriceCategoryResponseModel[] = [
      {
        id: 1,
        hasStocks: false,
        label: 'Plein tarif',
        price: 20,
      },
    ]

    const result = toFormValues(offer, priceCategories, context)

    expect(result.priceCategories).toHaveLength(1)
    expect(result.priceCategories[0].label).toBe('Plein tarif')
    expect(result.priceCategories[0].offerId).toBe(offer.id)
  })

  it('should create a default entry with label for empty event offer', () => {
    const offer = { ...baseOffer, isEvent: true }
    const context = makeContext(offer)

    const result = toFormValues(offer, [], context)

    expect(result.priceCategories).toHaveLength(1)
    expect(result.priceCategories[0].label).toBe('Tarif unique')
    expect(result.priceCategories[0].offerId).toBe(offer.id)
  })

  it('should create a default entry with null label for empty non-event offer', () => {
    const offer = { ...baseOffer, isEvent: false }
    const context = makeContext(offer)

    const result = toFormValues(offer, [], context)

    expect(result.priceCategories).toHaveLength(1)
    expect(result.priceCategories[0].label).toBeNull()
  })
})
