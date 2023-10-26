import { OfferStatus } from 'apiClient/v1'

import { getStockWarningText } from '../StockSection'

describe('getStockWarningText', () => {
  const testData = [
    {
      offerStatus: OfferStatus.SOLD_OUT,
      stocksCount: 1,
      expected: 'Votre stock est épuisé.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      stocksCount: 1,
      expected: 'Votre stock est expiré.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      stocksCount: 0,
      expected: 'Vous n’avez aucun stock renseigné.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      stocksCount: null,
      expected: 'Vous n’avez aucun stock renseigné.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      stocksCount: undefined,
      expected: 'Vous n’avez aucun stock renseigné.',
    },
    {
      offerStatus: OfferStatus.INACTIVE,
      stocksCount: 1,
      expected: false,
    },
  ]
  it.each(testData)(
    'should render $expected',
    ({ offerStatus, stocksCount, expected }) => {
      const result = getStockWarningText(offerStatus, stocksCount)

      expect(result).toStrictEqual(expected)
    }
  )
})
