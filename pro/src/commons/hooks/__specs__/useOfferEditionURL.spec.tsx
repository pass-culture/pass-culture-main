import { CollectiveOfferStatus } from 'apiClient/v1'

import { useOfferEditionURL } from '../useOfferEditionURL'

describe('useOfferEditionURL', () => {
  it('should return right url when offer is individual', () => {
    const offerId = 3

    const urlResult = useOfferEditionURL({
      isOfferEducational: false,
      offerId,
    })

    expect(urlResult).toStrictEqual(
      `/offre/individuelle/${offerId}/recapitulatif/details`
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

  it('should return right url when offer is collective and status is draft', () => {
    const offerId = 3

    const urlResult = useOfferEditionURL({
      isOfferEducational: true,
      offerId,
      status: CollectiveOfferStatus.DRAFT,
    })

    expect(urlResult).toStrictEqual(`/offre/collectif/${offerId}/creation`)
  })
})
