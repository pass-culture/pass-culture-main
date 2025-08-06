import { OfferStatus } from '@/apiClient//v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { getStockWarningText } from '../getStockWarningText'

describe('getStockWarningText', () => {
  const testData = [
    {
      offerStatus: OfferStatus.SOLD_OUT,
      hasStocks: true,
      expected: 'Votre stock est épuisé.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      hasStocks: true,
      expected: 'Votre stock est expiré.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      hasStocks: false,
      expected: 'Vous n’avez aucun stock renseigné.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      hasStocks: false,
      expected: 'Vous n’avez aucun stock renseigné.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      hasStocks: false,
      expected: 'Vous n’avez aucun stock renseigné.',
    },
    {
      offerStatus: OfferStatus.INACTIVE,
      hasStocks: true,
      expected: false,
    },
  ]
  it.each(testData)(
    'should render $expected',
    ({ offerStatus, hasStocks, expected }) => {
      const result = getStockWarningText(
        getIndividualOfferFactory({ status: offerStatus, hasStocks })
      )

      expect(result).toStrictEqual(expected)
    }
  )
})
