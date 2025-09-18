import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { saveEventOfferPriceTable } from '../saveEventOfferPriceTable'

vi.mock('@/apiClient/api', () => ({
  api: {
    patchOffer: vi.fn(),
    postPriceCategories: vi.fn(),
  },
}))

import { api } from '@/apiClient/api'

describe('saveEventOfferPriceTable', () => {
  const offer = getIndividualOfferFactory()
  const formValues = {
    entries: [
      {
        activationCodes: [],
        activationCodesExpirationDatetime: '',
        bookingLimitDatetime: '',
        bookingsQuantity: null,
        hasActivationCode: false,
        id: null,
        label: 'Normal',
        price: 10,
        quantity: 5,
        offerId: offer.id,
        remainingQuantity: null,
      },
    ],
    isDuo: true,
  }

  it('should patch offer and post price categories', async () => {
    await saveEventOfferPriceTable(formValues, { offer })

    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, { isDuo: true })
    expect(api.postPriceCategories).toHaveBeenCalledWith(
      offer.id,
      expect.objectContaining({ priceCategories: expect.any(Array) })
    )
  })
})
