import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'

import Support from '../Support'

const mockLogEvent = jest.fn()

const renderSupport = () => {
  return render(
    <MemoryRouter initialEntries={['/accueil']}>
      <Support />
    </MemoryRouter>
  )
}

describe('homepage: ProfileAndSupport: Support', () => {
  describe('render', () => {
    it('should display help links', () => {
      renderSupport()
      const contactLink = screen.getByText('Contacter le support')
      const cguLink = screen.getByText('Conditions Générales d’Utilisation')
      const helpCenterLink = screen.getByText('Centre d’aide')

      expect(contactLink).toBeInTheDocument()
      expect(cguLink).toBeInTheDocument()
      expect(helpCenterLink).toBeInTheDocument()

      expect(contactLink.getAttribute('href')).toBe(
        'mailto:support-pro@passculture.app'
      )
      expect(cguLink.getAttribute('href')).toBe(
        'https://pass.culture.fr/cgu-professionnels/'
      )
      expect(helpCenterLink.getAttribute('href')).toBe(
        'https://aide.passculture.app'
      )
    })

    it('should trigger events when clicking on link', async () => {
      jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
      renderSupport()
      const contactLink = screen.getByText('Contacter le support')
      const cguLink = screen.getByText('Conditions Générales d’Utilisation')
      const helpCenterLink = screen.getByText('Centre d’aide')

      await userEvent.click(contactLink)
      await userEvent.click(cguLink)
      await userEvent.click(helpCenterLink)

      expect(mockLogEvent).toHaveBeenCalledTimes(3)
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
    })
  })
})
