import { describe } from 'vitest'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  priceCategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'

import type { PriceTableFormContext } from '../types'
import { toFormValues } from '../utils/toFormValues'

const buildContext = (
  overrides: Partial<PriceTableFormContext> = {}
): PriceTableFormContext => {
  const offer = getIndividualOfferFactory({
    isEvent: overrides.offer?.isEvent ?? true,
  })

  return {
    isCaledonian: false,
    mode: OFFER_WIZARD_MODE.CREATION,
    offer,
    ...overrides,
  }
}

const baseContext = buildContext()

const baseOffer = getIndividualOfferFactory({ id: 1 })
const basePriceCateogry = priceCategoryFactory()

describe('toFormValues', () => {
  it(`should cast and keep price in EUR when not isCaledonian`, () => {
    const context = {
      ...baseContext,
      isCaledonian: false,
    }
    const offer = {
      ...baseOffer,
    }
    const priceCategory = { ...basePriceCateogry, price: 20 }
    const priceCategories = [priceCategory]
    const formValues = toFormValues(offer, priceCategories, context)
    expect(formValues.entries[0].price).toBe(20)
  })

  it(`should cast and convert price from EUR to XPF when isCaledonian`, () => {
    const context = {
      ...baseContext,
      isCaledonian: true,
    }
    const offer = {
      ...baseOffer,
    }
    const priceCategory = { ...basePriceCateogry, price: 20 }
    const priceCategories = [priceCategory]
    const formValues = toFormValues(offer, priceCategories, context)
    expect(formValues.entries[0].price).toBe(2385)
  })
})
