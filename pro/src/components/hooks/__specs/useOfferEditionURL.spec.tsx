import { useOfferEditionURL } from '../useOfferEditionURL'

describe('useOfferEditionURL', () => {
  test('It should retrun right url when offer is educational', () => {
    const isOfferEducational = true
    const offerId = 'offerID'
    const useSummaryPage = false
    const isShowcase = false

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      useSummaryPage,
      isShowcase
    )

    expect(urlResutl).toStrictEqual('/offre/offerID/collectif/edition')
  })

  test('It should retrun right url when offer is educational and showcase', () => {
    const isOfferEducational = true
    const offerId = 'offerID'
    const useSummaryPage = false
    const isShowcase = true

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      useSummaryPage,
      isShowcase
    )

    expect(urlResutl).toStrictEqual('/offre/T-offerID/collectif/edition')
  })

  test('It should retrun right url when offer is individual and summary page is activated', () => {
    const isOfferEducational = false
    const offerId = 'offerID'
    const useSummaryPage = true
    const isShowcase = false

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      useSummaryPage,
      isShowcase
    )

    expect(urlResutl).toStrictEqual('/offre/offerID/individuel/recapitulatif')
  })

  test('It should retrun right url when offer is individual and summary page is not activated', () => {
    const isOfferEducational = false
    const offerId = 'offerID'
    const useSummaryPage = false
    const isShowcase = false

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      useSummaryPage,
      isShowcase
    )

    expect(urlResutl).toStrictEqual('/offre/offerID/individuel/edition')
  })
})
