import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { HighlightEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import {
  OfferHighlightCard,
  type OfferHighlightCardProps,
} from './OfferHighlightCard'

const mockLogEvent = vi.fn()

vi.mock('@/apiClient/api', () => ({
  api: {
    getHighlights: vi.fn(),
  },
}))

function renderOfferHighlightCard(props: OfferHighlightCardProps) {
  return renderWithProviders(
    <>
      <OfferHighlightCard {...props} />
      <SnackBarContainer />
    </>
  )
}

describe('OfferHighlightCard', () => {
  describe('when no highlight request', () => {
    it('should display the card with text and action button', () => {
      renderOfferHighlightCard({ offerId: 1, highlightRequests: [] })

      expect(
        screen.getByText(
          'Valorisez votre évènement en l’associant à un temps fort.'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Relier l’offre à un temps fort' })
      ).toBeInTheDocument()
    })

    it('should open the modal when clicking the button and log', async () => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
      vi.spyOn(api, 'getHighlights').mockResolvedValueOnce([])

      renderOfferHighlightCard({ offerId: 1, highlightRequests: [] })
      await userEvent.click(
        screen.getByRole('button', { name: 'Relier l’offre à un temps fort' })
      )

      expect(
        screen.getByRole('heading', { name: 'Choisir un temps fort' })
      ).toBeInTheDocument()
      expect(mockLogEvent).toBeCalledWith(
        HighlightEvents.HAS_CLICKED_CHOOSE_HIGHLIGHT,
        { offerId: 1 }
      )
    })
  })

  describe('when offer has highlight request', () => {
    it('should display the card with text and edit button', () => {
      renderOfferHighlightCard({
        offerId: 1,
        highlightRequests: [{ id: 666, name: 'Journée de la révolution' }],
      })

      expect(screen.getByText('Valorisation à venir :')).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Modifier' })
      ).toBeInTheDocument()
    })

    it('should display the card with plural when multiple requests', () => {
      renderOfferHighlightCard({
        offerId: 1,
        highlightRequests: [
          { id: 666, name: 'Journée de la révolution' },
          { id: 667, name: 'Nowel' },
        ],
      })

      expect(screen.getByText('Valorisations à venir :')).toBeInTheDocument()
    })

    it('should open the modal when clicking the button and log edit event', async () => {
      vi.spyOn(api, 'getHighlights').mockResolvedValueOnce([])
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
      renderOfferHighlightCard({
        offerId: 1,
        highlightRequests: [{ id: 666, name: 'Journée de la révolution' }],
      })
      await userEvent.click(screen.getByRole('button', { name: 'Modifier' }))

      expect(
        screen.getByRole('heading', { name: 'Choisir un temps fort' })
      ).toBeInTheDocument()
      expect(mockLogEvent).toBeCalledWith(
        HighlightEvents.HAS_CLICKED_EDIT_HIGHLIGHT,
        { offerId: 1, hightlightIds: [666] }
      )
    })
  })
})
