import React from 'react'
import { describe, expect, it, vi } from 'vitest'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
} from 'apiClient/v1'

import { createCollectiveOfferColumns } from './createCollectiveOfferColumns'

// -----------------------------------------------------------------------------
// Mocks
// -----------------------------------------------------------------------------
vi.mock('commons/hooks/useActiveFeature', () => ({
  useActiveFeature: () => true, // always enable the new detail page in tests
}))

vi.mock(
  'commons/core/OfferEducational/utils/computeURLCollectiveOfferId',
  () => ({
    // make the helper predictable in tests
    computeURLCollectiveOfferId: (id: number | string) => String(id),
  })
)

// The ExpirationCell returns a real React element in production.
// We only care that *something* is rendered, so stub it out here.
vi.mock('./ExpirationCell/ExpirationCell', () => ({
  ExpirationCell: () => <div>ExpirationCell</div>,
}))

// -----------------------------------------------------------------------------
// Test helpers
// -----------------------------------------------------------------------------
const createOffer = (
  partial: Partial<CollectiveOfferResponseModel> = {}
): CollectiveOfferResponseModel =>
  ({
    id: 1,
    name: 'My little offer',
    isShowcase: false,
    displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
    imageUrl: null,
    stocks: [],
    venue: {
      name: 'Venue',
      isVirtual: false,
      offererName: 'Offerer',
      publicName: null,
    },
    educationalInstitution: null,
    allowedActions: [],
    // everything else can be undefined – we cast at the end
    ...partial,
  }) as unknown as CollectiveOfferResponseModel

// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

describe('createCollectiveOfferColumns()', () => {
  const factoryParams = {
    selectedIds: new Set<string | number>(),
    toggleSelect: () => undefined,
    urlSearchFilters: {},
  }

  it('returns the expected column layout', () => {
    const { columns } = createCollectiveOfferColumns(factoryParams)

    expect(columns).toHaveLength(8)
    expect(columns.map((c) => c.id)).toEqual([
      'offerHeader',
      'offer-head-thumb',
      'offer-head-name',
      'offer-head-event-date',
      'offer-head-structure',
      'offer-head-institution',
      'offer-head-status',
      'offer-head-actions',
    ])

    // the grouped header on the first column
    const [groupHeader] = columns
    expect(groupHeader.headerColSpan).toBe(2)
    expect(groupHeader.bodyHidden).toBe(true)
  })

  describe('getRowLink()', () => {
    it('points to the recap page for a published offer', () => {
      const offer = createOffer({
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      })
      const { getRowLink } = createCollectiveOfferColumns(factoryParams)

      expect(getRowLink(offer)).toBe('/offre/1/collectif/recapitulatif')
    })

    it('points to the creation flow for a draft offer', () => {
      const offer = createOffer({
        displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
      })
      const { getRowLink } = createCollectiveOfferColumns(factoryParams)

      expect(getRowLink(offer)).toBe('/offre/collectif/1/creation')
    })
  })

  describe('getExpandedContent()', () => {
    it('renders an ExpirationCell when the bookable offer is PUBLISHED with a booking limit date', () => {
      const offer = createOffer({
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        stocks: [
          {
            // @ts-expect-error – we only need the field used by the component
            bookingLimitDatetime: new Date().toISOString(),
          },
        ],
      })
      const { getExpandedContent } = createCollectiveOfferColumns(factoryParams)

      const node = getExpandedContent(offer)
      expect(React.isValidElement(node)).toBe(true)
      if (React.isValidElement(node)) {
        // With our stub, the type is the anonymous component we returned.
        expect(node.props.rowId).toBe('collective-offer-1')
      }
    })

    it('returns null for showcase offers', () => {
      const offer = createOffer({
        isShowcase: true,
        stocks: [
          {
            // @ts-expect-error – we only need the field used by the component
            bookingLimitDatetime: new Date().toISOString(),
          },
        ],
      })
      const { getExpandedContent } = createCollectiveOfferColumns(factoryParams)

      expect(getExpandedContent(offer)).toBeNull()
    })
  })
})
