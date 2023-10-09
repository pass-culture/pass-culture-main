import { useOfferEditionURL } from '../useOfferEditionURL'

describe('useOfferEditionURL', () => {
  it('should return right url when offer is individual', () => {
    const isOfferEducational = false
    const offerId = 3
    const isShowcase = false

    const urlResult = useOfferEditionURL(
      isOfferEducational,
      offerId,
      isShowcase
    )

    expect(urlResult).toStrictEqual(
      `/offre/individuelle/${offerId}/recapitulatif`
    )
  })
})
