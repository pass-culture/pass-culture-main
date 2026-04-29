import type { UseFormReturn } from 'react-hook-form'
import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import type { PriceTableFormValues } from '../../schemas'
import { saveNonEventOfferPriceTable } from '../saveNonEventOfferPriceTable'

vi.mock('swr', async (importOriginal) => ({
  ...(await importOriginal()),
  mutate: vi.fn(),
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    patchOffer: vi.fn(),
    upsertOfferStocks: vi.fn(),
  },
}))

describe('saveNonEventOfferPriceTable', () => {
  const offer = getIndividualOfferFactory()
  const formValues = {
    priceCategories: [
      {
        activationCodes: [],
        activationCodesExpirationDatetime: '',
        bookingLimitDatetime: '',
        bookingsQuantity: null,
        hasActivationCode: false,
        hasStocks: null,
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
        priceCategories: true,
      },
    },
  }

  it('should patch offer and upsert stocks', async () => {
    await saveNonEventOfferPriceTable(
      formValues,
      form as unknown as UseFormReturn<PriceTableFormValues>,
      { offer }
    )

    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, { isDuo: true })
    expect(api.upsertOfferStocks).toHaveBeenCalledWith(
      offer.id,
      expect.objectContaining({ stocks: expect.any(Array) })
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
    await saveNonEventOfferPriceTable(
      formValues,
      form as unknown as UseFormReturn<PriceTableFormValues>,
      { offer }
    )

    expect(api.patchOffer).toHaveBeenCalledWith(offer.id, { isDuo: true })
  })

  it('should revalidate offer data after upserting stocks', async () => {
    await saveNonEventOfferPriceTable(
      formValues,
      form as unknown as UseFormReturn<PriceTableFormValues>,
      { offer }
    )

    expect(mutate).toHaveBeenCalledWith([GET_OFFER_QUERY_KEY, offer.id])
  })
})
