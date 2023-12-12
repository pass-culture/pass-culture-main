import { OfferStatus } from 'apiClient/v1'

import { getStockWarningText } from '../StockSection'

describe('getStockWarningText', () => {
  const testData = [
    {
      offerStatus: OfferStatus.SOLD_OUT,
      hasStock: true,
      expected: 'Votre stock est épuisé.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      hasStock: true,
      expected: 'Votre stock est expiré.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      hasStock: false,
      expected: 'Vous n’avez aucun stock renseigné.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      hasStock: null,
      expected: 'Vous n’avez aucun stock renseigné.',
    },
    {
      offerStatus: OfferStatus.EXPIRED,
      hasStock: undefined,
      expected: 'Vous n’avez aucun stock renseigné.',
    },
    {
      offerStatus: OfferStatus.INACTIVE,
      hasStock: true,
      expected: false,
    },
  ]
  it.each(testData)(
    'should render $expected',
    ({ offerStatus, hasStock, expected }) => {
      const result = getStockWarningText(offerStatus, hasStock)

      expect(result).toStrictEqual(expected)
    }
  )
})
