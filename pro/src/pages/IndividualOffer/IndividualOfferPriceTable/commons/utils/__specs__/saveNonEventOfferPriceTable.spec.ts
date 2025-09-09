import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { saveNonEventOfferPriceTable } from '../saveNonEventOfferPriceTable'

vi.mock('@/apiClient/api', () => ({
  api: {
    patchOffer: vi.fn(),
    updateThingStock: vi.fn(),
    createThingStock: vi.fn(),
  },
}))

import { api } from '@/apiClient/api'

describe('saveNonEventOfferPriceTable', () => {
  const offer = getIndividualOfferFactory()
  const entryBase = {
    activationCodes: [],
    activationCodesExpirationDatetime: '',
    bookingLimitDatetime: '',
    bookingsQuantity: undefined,
    id: undefined,
    label: 'Normal',
    price: 10,
    quantity: 5,
    offerId: offer.id,
    remainingQuantity: null,
  }
  const formValuesBase = {
    entries: [entryBase],
    isDuo: true,
  }

  it('should create thing stock when first entry has no id', async () => {
    await saveNonEventOfferPriceTable(formValuesBase, {
      offer,
    })

    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, { isDuo: true })
    expect(api.createThingStock).toHaveBeenCalledWith(
      expect.objectContaining({ offerId: offer.id })
    )
  })

  it('should update thing stock when first entry has id', async () => {
    const formValues = {
      entries: [{ ...entryBase, id: 99 }],
      isDuo: true as boolean | null,
    }

    await saveNonEventOfferPriceTable(formValues, {
      offer,
    })

    expect(api.updateThingStock).toHaveBeenCalledWith(99, expect.any(Object))
  })
})
