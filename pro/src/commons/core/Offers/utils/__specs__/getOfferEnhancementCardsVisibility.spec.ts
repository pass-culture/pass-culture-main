import { OfferStatus } from '@/apiClient/v1'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'

import { getOfferEnhancementActionsVisibility } from '../getOfferEnhancementActionsVisibility'

describe('getOfferEnhancementActionsVisibility', () => {
  it('hide all actions when offer is null', () => {
    expect(getOfferEnhancementActionsVisibility(null)).toEqual({
      shouldDisplayRecommendationAction: false,
      shouldDisplayHighlightAction: false,
      shouldDisplayHeadlineAction: false,
    })
  })

  it('displays all actions for an active event offer', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.ACTIVE,
      isEvent: true,
    })

    const result = getOfferEnhancementActionsVisibility(offer)

    expect(result.shouldDisplayRecommendationAction).toBe(true)
    expect(result.shouldDisplayHighlightAction).toBe(true)
    expect(result.shouldDisplayHeadlineAction).toBe(true)
  })

  describe.each([OfferStatus.PENDING, OfferStatus.REJECTED, OfferStatus.DRAFT])(
    'when status is %s',
    (status) => {
      it('hides all Actions', () => {
        const offer = getIndividualOfferFactory({ status, isEvent: true })

        const result = getOfferEnhancementActionsVisibility(offer)

        expect(result.shouldDisplayRecommendationAction).toBe(false)
        expect(result.shouldDisplayHighlightAction).toBe(false)
        expect(result.shouldDisplayHeadlineAction).toBe(false)
      })
    }
  )

  it('hide headline Action when offer is not active', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.PUBLISHED,
      isEvent: true,
    })

    const result = getOfferEnhancementActionsVisibility(offer)

    expect(result.shouldDisplayHeadlineAction).toBe(false)
    expect(result.shouldDisplayRecommendationAction).toBe(true)
    expect(result.shouldDisplayHighlightAction).toBe(true)
  })

  it('hide headline Action when offer is imageless and product-based', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.ACTIVE,
      productId: 12,
      // TODO (tpommellet) to remove once GetIndividualOfferWithAddressResponseModel is migrated to Pydantic V2
      // @ts-expect-error
      thumbUrl: null,
    })

    const result = getOfferEnhancementActionsVisibility(offer)

    expect(result.shouldDisplayHeadlineAction).toBe(false)
    expect(result.shouldDisplayRecommendationAction).toBe(true)
    expect(result.shouldDisplayHighlightAction).toBe(true)
  })

  it('hide highlight Action when offer is not an event', () => {
    const offer = getIndividualOfferFactory({
      status: OfferStatus.ACTIVE,
      isEvent: false,
    })

    const result = getOfferEnhancementActionsVisibility(offer)

    expect(result.shouldDisplayHeadlineAction).toBe(true)
    expect(result.shouldDisplayRecommendationAction).toBe(true)
    expect(result.shouldDisplayHighlightAction).toBe(false)
  })
})
