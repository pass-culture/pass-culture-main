import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import {
  OfferHighlightBanner,
  type OfferHighlightBannerProps,
} from './OfferHighlightBanner'

vi.mock('@/apiClient/api', () => ({
  api: {
    getHighlights: vi.fn(),
  },
}))

function renderOfferHighlightBanner(props: OfferHighlightBannerProps) {
  return renderWithProviders(
    <>
      <OfferHighlightBanner {...props} />
      <Notification />
    </>
  )
}

describe('OfferHighlightBanner', () => {
  describe('when no highlight request', () => {
    it('should display the banner with text and button', () => {
      renderOfferHighlightBanner({ offerId: 1, highlightRequests: [] })

      expect(
        screen.getByText(
          'Valorisez votre évènement en l’associant à un temps fort.'
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Choisir un temps fort' })
      ).toBeInTheDocument()
    })

    it('should open the modal when clicking the button', async () => {
      vi.spyOn(api, 'getHighlights').mockResolvedValueOnce([])

      renderOfferHighlightBanner({ offerId: 1, highlightRequests: [] })
      await userEvent.click(
        screen.getByRole('button', { name: 'Choisir un temps fort' })
      )

      expect(
        screen.getByRole('heading', { name: 'Choisir un temps fort' })
      ).toBeInTheDocument()
    })
  })

  describe('when offer ha highlight request', () => {
    it('should display the banner with text and button', () => {
      renderOfferHighlightBanner({
        offerId: 1,
        highlightRequests: [{ id: 666, name: 'Journée de la révolution' }],
      })

      expect(screen.getByText('Valorisation à venir :')).toBeInTheDocument()
      expect(screen.getByText('Journée de la révolution')).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Éditer le temps fort' })
      ).toBeInTheDocument()
    })

    it('should display the banner with text and button with plural', () => {
      renderOfferHighlightBanner({
        offerId: 1,
        highlightRequests: [
          { id: 666, name: 'Journée de la révolution' },
          { id: 667, name: 'Nowel' },
        ],
      })

      expect(screen.getByText('Valorisations à venir :')).toBeInTheDocument()
      expect(screen.getByText('Journée de la révolution')).toBeInTheDocument()
      expect(screen.getByText('Nowel')).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'Éditer les temps forts' })
      ).toBeInTheDocument()
    })

    it('should open the modal when clicking the button', async () => {
      vi.spyOn(api, 'getHighlights').mockResolvedValueOnce([])

      renderOfferHighlightBanner({
        offerId: 1,
        highlightRequests: [{ id: 666, name: 'Journée de la révolution' }],
      })
      await userEvent.click(
        screen.getByRole('button', { name: 'Éditer le temps fort' })
      )

      expect(
        screen.getByRole('heading', { name: 'Choisir un temps fort' })
      ).toBeInTheDocument()
    })
  })
})
