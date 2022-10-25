import { useOfferEditionURL } from '../useOfferEditionURL'

describe('useOfferEditionURL', () => {
  test('It should retrun right url when offer is educational', () => {
    const isOfferEducational = true
    const offerId = 'offerID'
    const isOfferFormV3 = false
    const isShowcase = false

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      isOfferFormV3,
      isShowcase
    )

    expect(urlResutl).toStrictEqual('/offre/offerID/collectif/recapitulatif')
  })

  test('It should retrun right url when offer is educational and showcase', () => {
    const isOfferEducational = true
    const offerId = 'offerID'
    const isOfferFormV3 = false
    const isShowcase = true

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      isOfferFormV3,
      isShowcase
    )

    expect(urlResutl).toStrictEqual('/offre/T-offerID/collectif/recapitulatif')
  })

  test('It should retrun right url when offer is individual and offerFormV3 is activated', () => {
    const isOfferEducational = false
    const offerId = 'offerID'
    const isOfferFormV3 = true
    const isShowcase = false

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      isOfferFormV3,
      isShowcase
    )

    expect(urlResutl).toStrictEqual(
      '/offre/offerID/v3/individuelle/recapitulatif'
    )
  })

  test('It should retrun right url when offer is individual and offerFormV3 is not activated (v2)', () => {
    const isOfferEducational = false
    const offerId = 'offerID'
    const isOfferFormV3 = false
    const isShowcase = false

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      isOfferFormV3,
      isShowcase
    )

    expect(urlResutl).toStrictEqual('/offre/offerID/individuel/recapitulatif')
  })

  test('It should retrun right url when offer is an individual draft (v2)', () => {
    const isOfferEducational = false
    const offerId = 'offerID'
    const isOfferFormV3 = false
    const isShowcase = false

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      isOfferFormV3,
      isShowcase,
      'DRAFT'
    )

    expect(urlResutl).toStrictEqual('/offre/offerID/individuel/brouillon')
  })

  test('It should retrun right url when offer is an individual draft', () => {
    const isOfferEducational = false
    const offerId = 'offerID'
    const isOfferFormV3 = true
    const isShowcase = false

    const urlResutl = useOfferEditionURL(
      isOfferEducational,
      offerId,
      isOfferFormV3,
      isShowcase,
      'DRAFT'
    )

    expect(urlResutl).toStrictEqual(
      '/offre/offerID/v3/brouillon/individuelle/informations'
    )
  })
})
