import type { UseFormReturn } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import type { PriceTableFormValues } from '../../schemas'
import { saveEventOfferPriceTable } from '../saveEventOfferPriceTable'

vi.mock('@/apiClient/api', () => ({
  api: {
    patchOffer: vi.fn(),
    upsertOfferPriceCategories: vi.fn(),
  },
}))

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

  const form = {
    formState: {
      dirtyFields: {
        isDuo: true,
        entries: true,
      },
    },
  }
  it('should patch offer and post price categories', async () => {
    await saveEventOfferPriceTable(
      formValues,
      form as unknown as UseFormReturn<PriceTableFormValues>,
      { offer }
    )

    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, { isDuo: true })
    expect(api.upsertOfferPriceCategories).toHaveBeenCalledWith(
      offer.id,
      expect.objectContaining({ priceCategories: expect.any(Array) })
    )
  })

  it('should only patch offer when only isDuo is dirty', async () => {
    const form = {
      formState: {
        dirtyFields: {
          isDuo: true,
        },
      },
    }
    await saveEventOfferPriceTable(
      formValues,
      form as unknown as UseFormReturn<PriceTableFormValues>,
      { offer }
    )

    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, { isDuo: true })
  })

  it('should only post price categories when only entries are dirty', async () => {
    const form = {
      formState: {
        dirtyFields: true,
      },
    }

    await saveEventOfferPriceTable(
      formValues,
      form as unknown as UseFormReturn<PriceTableFormValues>,
      { offer }
    )

    expect(api.patchOffer).not.toHaveBeenCalled()
    expect(api.upsertOfferPriceCategories).toHaveBeenCalledWith(
      offer.id,
      expect.objectContaining({ priceCategories: expect.any(Array) })
    )
  })
})
