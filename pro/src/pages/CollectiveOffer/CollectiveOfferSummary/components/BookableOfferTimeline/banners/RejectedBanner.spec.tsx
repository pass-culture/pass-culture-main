import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { CollectiveOfferDisplayedStatus } from '@/apiClient//v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import * as duplicateBookableOffer from '@/commons/core/OfferEducational/utils/duplicateBookableOffer'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { RejectedBanner } from './RejectedBanner'

describe('RejectedBanner', () => {
  const mockLogEvent = vi.fn()
  const mockDuplicateBookableOffer = vi.fn().mockResolvedValue(undefined)

  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      ...vi.importActual('@/app/App/analytics/firebase'),
      logEvent: mockLogEvent,
    }))

    vi.spyOn(
      duplicateBookableOffer,
      'duplicateBookableOffer'
    ).mockImplementation(mockDuplicateBookableOffer)
  })

  it('should log event on press Dupliquer', async () => {
    renderWithProviders(<RejectedBanner offerId={2} />)

    const duplicateButton = screen.getByText("Dupliquer l'offre")
    await userEvent.click(duplicateButton)

    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DUPLICATE_BOOKABLE_OFFER,
      {
        from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_TIMELINE,
        offerId: 2,
        offerType: 'collective',
        offerStatus: CollectiveOfferDisplayedStatus.REJECTED,
      }
    )
  })

  it('should duplicate offer on press Dupliquer', async () => {
    renderWithProviders(<RejectedBanner offerId={2} />)

    const duplicateButton = screen.getByText("Dupliquer l'offre")
    await userEvent.click(duplicateButton)

    expect(mockDuplicateBookableOffer).toHaveBeenCalledTimes(1)
  })
})
