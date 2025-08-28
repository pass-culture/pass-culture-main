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
        bookingsQuantity: undefined,
        id: undefined,
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

  it('should handle errors', async () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {})
    vi.spyOn(api, 'patchOffer').mockRejectedValueOnce('An error')

    await saveEventOfferPriceTable(formValues, { offer })

    expect(api.postPriceCategories).not.toHaveBeenCalled()
    expect(consoleErrorSpy).toHaveBeenCalledWith('An error')
  })
})
