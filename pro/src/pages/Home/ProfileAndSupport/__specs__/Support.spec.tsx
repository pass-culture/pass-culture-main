import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Support } from '../Support'

const mockLogEvent = vi.fn()

const renderSupport = (storeOverrides: any = {}) => {
  return renderWithProviders(<Support />, {
    storeOverrides,
    initialRouterEntries: ['/accueil'],
  })
}

describe('homepage: ProfileAndSupport: Support', () => {
  describe('render', () => {
    it('should display help links', async () => {
      renderSupport()
      const contactLink = screen.getByText(
        'Contacter le support par mail à support-pro@passculture.app'
      )
      const cguLink = screen.getByText('Conditions Générales d’Utilisation')
      const helpCenterLink = screen.getByText('Centre d’aide')
      const bestPracticesLink = screen.getByText('Bonnes pratiques et études')

      expect(contactLink).toBeInTheDocument()
      expect(cguLink).toBeInTheDocument()
      expect(helpCenterLink).toBeInTheDocument()
      expect(bestPracticesLink).toBeInTheDocument()

      expect(contactLink.getAttribute('href')).toBe(
        'mailto:support-pro@passculture.app'
      )
      expect(cguLink.getAttribute('href')).toBe(
        'https://pass.culture.fr/cgu-professionnels/'
      )
      expect(helpCenterLink.getAttribute('href')).toBe(
        'https://aide.passculture.app'
      )
      expect(bestPracticesLink.getAttribute('href')).toBe(
        'https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0'
      )
      expect(await screen.findByText(/Gestion des cookies/)).toBeInTheDocument()
    })

    it('should trigger events when clicking on link', async () => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
      renderSupport()
      const contactLink = screen.getByText(
        'Contacter le support par mail à support-pro@passculture.app'
      )
      const cguLink = screen.getByText('Conditions Générales d’Utilisation')
      const helpCenterLink = screen.getByText('Centre d’aide')
      const bestPracticesLink = screen.getByText('Bonnes pratiques et études')

      await userEvent.click(contactLink)
      await userEvent.click(cguLink)
      await userEvent.click(helpCenterLink)
      await userEvent.click(bestPracticesLink)

      expect(mockLogEvent).toHaveBeenCalledTimes(4)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_CONSULT_SUPPORT,
        { from: '/accueil' }
      )
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        2,
        Events.CLICKED_CONSULT_CGU,
        { from: '/accueil' }
      )
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        3,
        Events.CLICKED_HELP_CENTER,
        { from: '/accueil' }
      )
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        4,
        Events.CLICKED_BEST_PRACTICES_STUDIES,
        { from: '/accueil' }
      )
    })
  })
})
