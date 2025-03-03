import { collectiveOfferFactory } from 'commons/utils/factories/collectiveApiFactories'
import { listOffersOfferFactory } from 'commons/utils/factories/individualApiFactories'

import { isSameOffer } from '../isSameOffer'

describe('isSameOffer', () => {
  const individualOffer = listOffersOfferFactory()
  const collectiveOfferBookable = collectiveOfferFactory({ isShowcase: false })
  const collectiveOfferTemplate = collectiveOfferFactory({ isShowcase: true })

  it('should verify that two offers are the same', () => {
    expect(isSameOffer(individualOffer, collectiveOfferBookable)).toEqual(false)

    expect(isSameOffer({ ...individualOffer }, { ...individualOffer })).toEqual(
      true
    )
    expect(
      isSameOffer({ ...individualOffer, id: 1 }, { ...individualOffer, id: 2 })
    ).toEqual(false)

    expect(
      isSameOffer(
        { ...collectiveOfferBookable },
        { ...collectiveOfferBookable }
      )
    ).toEqual(true)
    expect(
      isSameOffer(
        { ...collectiveOfferBookable, id: 1 },
        { ...collectiveOfferBookable, id: 2 }
      )
    ).toEqual(false)

    expect(
      isSameOffer(collectiveOfferBookable, collectiveOfferTemplate)
    ).toEqual(false)
    expect(
      isSameOffer(
        { ...collectiveOfferBookable, id: 1 },
        { ...collectiveOfferTemplate, id: 1 }
      )
    ).toEqual(false)

    expect(
      isSameOffer(
        { ...collectiveOfferTemplate },
        { ...collectiveOfferTemplate }
      )
    ).toEqual(true)
    expect(
      isSameOffer(
        { ...collectiveOfferTemplate, id: 1 },
        { ...collectiveOfferTemplate, id: 2 }
      )
    ).toEqual(false)
  })
})
