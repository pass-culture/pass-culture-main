import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { EditoCard } from './EditoCard'

const mockLogEvent = vi.fn()

vi.mock('../HighlightHome/ModalHighlight/ModalHighlight', () => ({
  ModalHighlight: ({ trigger }: { trigger: React.ReactNode }) => <>{trigger}</>,
}))

const defaultProps = {
  venueId: 1,
  canDisplayHighlights: false,
}

describe('EditoCard', () => {
  it('should display the main title', () => {
    renderWithProviders(<EditoCard {...defaultProps} />)
    expect(
      screen.getByText('Comment valoriser vos offres auprès du public jeune ?')
    ).toBeVisible()
  })

  it('should always display the cultural survey card', () => {
    renderWithProviders(<EditoCard {...defaultProps} />)
    expect(
      screen.getByText(
        '[Enquête pass Culture] les 15-20 ans et leur rapport à la culture'
      )
    ).toBeVisible()
  })

  describe('when canDisplayHighlights is false', () => {
    it('should display the headline offer card', () => {
      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={false} />
      )
      expect(
        screen.getByText(
          "Mettez une offre en valeur sur votre page de l'application"
        )
      ).toBeVisible()
    })

    it('should display the recommendation card', () => {
      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={false} />
      )
      expect(
        screen.getByText(
          'Écrivez une recommandation pour conseiller votre offre'
        )
      ).toBeVisible()
    })

    it('should not display the highlight offer card', () => {
      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={false} />
      )
      expect(
        screen.queryByText('Valoriser vos évènements sur le pass Culture !')
      ).not.toBeInTheDocument()
    })
  })

  describe('when canDisplayHighlights is true', () => {
    it('should display the highlight offer card', () => {
      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={true} />
      )
      expect(
        screen.getByText('Valoriser vos évènements sur le pass Culture !')
      ).toBeVisible()
    })

    it('should display the headline offer card', () => {
      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={true} />
      )
      expect(
        screen.getByText(
          "Mettez une offre en valeur sur votre page de l'application"
        )
      ).toBeVisible()
    })

    it('should not display the recommendation card', () => {
      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={true} />
      )
      expect(
        screen.queryByText(
          'Écrivez une recommandation pour conseiller votre offre'
        )
      ).not.toBeInTheDocument()
    })

    it('should display the highlights button', () => {
      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={true} />
      )
      expect(
        screen.getByRole('button', { name: 'Parcourir les temps forts' })
      ).toBeVisible()
    })
  })

  describe('cultural survey card', () => {
    it('should display a link to the survey that opens in a new tab', () => {
      renderWithProviders(<EditoCard {...defaultProps} />)
      const link = screen.getByRole('a', { name: /Lire l’enquête/ })
      expect(link).toHaveAttribute(
        'href',
        'https://pass.culture.fr/ressources/references-culturelles-best-of-2025'
      )
      expect(link).toHaveAttribute('target', '_blank')
    })
  })

  describe('headline offer card', () => {
    it('should have a link to offer page', () => {
      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={true} />
      )
      const links = screen.getAllByRole('link', { name: 'Choisir une offre' })
      expect(links[0]).toHaveAttribute('href', '/offres')
    })
  })

  describe('recommendation card', () => {
    it('should have a link to offer page', () => {
      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={false} />
      )
      const links = screen.getAllByRole('link', { name: 'Choisir une offre' })
      expect(links[1]).toHaveAttribute('href', '/offres')
    })
  })

  describe('highlight offer card', () => {
    it('should open the highlight modal and log ', async () => {
      const user = userEvent.setup()

      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
      vi.spyOn(api, 'getHighlights').mockResolvedValue([])

      renderWithProviders(
        <EditoCard {...defaultProps} canDisplayHighlights={true} />
      )

      await user.click(screen.getByText('Parcourir les temps forts'))

      expect(
        screen.getByRole('heading', {
          name: 'Qu’est-ce qu’un temps fort sur le pass Culture ?',
        })
      ).toBeInTheDocument()
      expect(mockLogEvent).toHaveBeenCalledWith(
        EngagementEvents.HAS_REQUESTED_HIGHLIGHTS,
        {
          venueId: 1,
          action: 'discover',
        }
      )
    })
  })
})
