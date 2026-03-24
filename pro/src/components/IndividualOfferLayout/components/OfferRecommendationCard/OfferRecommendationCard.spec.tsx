import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, vi } from 'vitest'

import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { OfferRecommendationCard } from './OfferRecommendationCard'

const mockLogEvent = vi.fn()

function renderOfferRecommendationCard() {
  return renderWithProviders(
    <>
      <OfferRecommendationCard offerId={769} />
      <SnackBarContainer />
    </>,
    {
      storeOverrides: {
        user: {
          selectedVenue: makeVenueListItem({ id: 2 }),
        },
      },
    }
  )
}

describe('OfferRecommendationCard', () => {
  describe('when no recommendation', () => {
    it('should display the card with placeholder text and add button', async () => {
      vi.spyOn(api, 'getOfferProAdvice').mockResolvedValue({ proAdvice: null })

      renderOfferRecommendationCard()

      await waitFor(() => {
        expect(
          screen.getByText(
            'Ajoutez une recommandation pour promouvoir votre offre'
          )
        ).toBeInTheDocument()
      })
      expect(
        screen.getByRole('button', { name: 'Ajouter une recommandation' })
      ).toBeInTheDocument()
    })
  })

  describe('when offer has recommendation', () => {
    it('should display the card with recommendation content and edit button', async () => {
      vi.spyOn(api, 'getOfferProAdvice').mockResolvedValue({
        proAdvice: {
          content: 'C’est génial !',
          author: 'Jean-Mi',
          updatedAt: '',
        },
      })

      renderOfferRecommendationCard()

      await waitFor(() => {
        expect(screen.getByText('Votre recommandation :')).toBeInTheDocument()
      })

      expect(screen.getByText('C’est génial !')).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Modifier' })
      ).toBeInTheDocument()
    })
  })

  it('should open the modal when clicking the creation button', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(api, 'getOfferProAdvice').mockResolvedValue({
      proAdvice: null,
    })

    renderOfferRecommendationCard()
    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter une recommandation' })
    )

    expect(
      screen.getByRole('heading', { name: 'Ajouter votre recommandation' })
    ).toBeInTheDocument()
    expect(mockLogEvent).toBeCalledWith(
      EngagementEvents.HAS_MADE_RECOMMENDATION,
      { offerId: 769, venueId: 2, action: 'started' }
    )
  })

  it('should open the modal when clicking the edition button', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(api, 'getOfferProAdvice').mockResolvedValue({
      proAdvice: {
        content: 'C’est génial !',
        author: 'Jean-Mi',
        updatedAt: '',
      },
    })

    renderOfferRecommendationCard()
    const editButton = await screen.findByRole('button', { name: 'Modifier' })
    await userEvent.click(editButton)

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Ajouter votre recommandation' })
      ).toBeInTheDocument()
    })
    expect(mockLogEvent).toBeCalledWith(
      EngagementEvents.HAS_MADE_RECOMMENDATION,
      { offerId: 769, venueId: 2, action: 'edited' }
    )
  })
})
