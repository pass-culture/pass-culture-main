import { OfferStatus } from '@/apiClient/v1/new'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { getOfferEnhancementCardsVisibility } from '../getOfferEnhancementCardsVisibility'

describe('getOfferEnhancementCardsVisibility', () => {
  it('hide all cards when offer is null', () => {
    expect(getOfferEnhancementCardsVisibility(null)).toEqual({
      shouldDisplayRecommendationCard: false,
      shouldDisplayHighlightCard: false,
      shouldDisplayHeadlineCard: false,
    })
  })

  it('displays all cards for an active event offer', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.ACTIVE,
      isEvent: true,
    })

    const result = getOfferEnhancementCardsVisibility(offer)

    expect(result.shouldDisplayRecommendationCard).toBe(true)
    expect(result.shouldDisplayHighlightCard).toBe(true)
    expect(result.shouldDisplayHeadlineCard).toBe(true)
  })

  describe.each([
    OfferStatus.PENDING,
    OfferStatus.REJECTED,
    OfferStatus.DRAFT,
  ])('when status is %s', (status) => {
    it('hides all cards', () => {
      const offer = getIndividualOfferFactory({ status, isEvent: true })

      const result = getOfferEnhancementCardsVisibility(offer)

      expect(result.shouldDisplayRecommendationCard).toBe(false)
      expect(result.shouldDisplayHighlightCard).toBe(false)
      expect(result.shouldDisplayHeadlineCard).toBe(false)
    })
  })

  it('hide headline card when offer is not active', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.PUBLISHED,
      isEvent: true,
    })

    const result = getOfferEnhancementCardsVisibility(offer)

    expect(result.shouldDisplayHeadlineCard).toBe(false)
    expect(result.shouldDisplayRecommendationCard).toBe(true)
    expect(result.shouldDisplayHighlightCard).toBe(true)
  })

  it('hide headline card when offer is imageless and product-based', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.ACTIVE,
      productId: 12,
      // TODO (tpommellet) to remove once GetIndividualOfferWithAddressResponseModel is migrated to Pydantic V2
      // @ts-expect-error
      thumbUrl: null,
    })

    const result = getOfferEnhancementCardsVisibility(offer)

    expect(result.shouldDisplayHeadlineCard).toBe(false)
    expect(result.shouldDisplayRecommendationCard).toBe(true)
    expect(result.shouldDisplayHighlightCard).toBe(true)
  })

  it('hide highlight card when offer is not an event', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.ACTIVE,
      isEvent: false,
    })

    const result = getOfferEnhancementCardsVisibility(offer)

    expect(result.shouldDisplayHeadlineCard).toBe(true)
    expect(result.shouldDisplayRecommendationCard).toBe(true)
    expect(result.shouldDisplayHighlightCard).toBe(false)
  })
})
