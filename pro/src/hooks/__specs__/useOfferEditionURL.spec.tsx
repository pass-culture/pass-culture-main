import { useOfferEditionURL } from '../useOfferEditionURL'

describe('useOfferEditionURL', () => {
  it('should return right url when offer is individual', () => {
    const offerId = 3

    const urlResult = useOfferEditionURL({
      isOfferEducational: false,
      offerId,
    })

    expect(urlResult).toStrictEqual(
      `/offre/individuelle/${offerId}/recapitulatif`
    )
  })

  it('should return right url when offer is collective', () => {
    const offerId = 3

    const urlResult = useOfferEditionURL({
      isOfferEducational: true,
      offerId,
    })

    expect(urlResult).toStrictEqual(`/offre/${offerId}/collectif/recapitulatif`)
  })

  it('should return right url when offer is showcase', () => {
    const offerId = 3

    const urlResult = useOfferEditionURL({
      isOfferEducational: true,
      offerId,
      isShowcase: true,
    })

    expect(urlResult).toStrictEqual(
      `/offre/T-${offerId}/collectif/recapitulatif`
    )
  })

  it('should return right url when offer is individual after split of offer', () => {
    const offerId = 3

    const urlResult = useOfferEditionURL({
      isOfferEducational: false,
      offerId,
      isSplitOfferEnabled: true,
    })

    expect(urlResult).toStrictEqual(`/offre/individuelle/${offerId}/details`)
  })
})
