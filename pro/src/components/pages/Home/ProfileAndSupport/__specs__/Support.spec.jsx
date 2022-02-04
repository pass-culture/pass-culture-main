import '@testing-library/jest-dom'
import { act, render, screen } from '@testing-library/react'
import React from 'react'

import Support from '../Support'

const renderSupport = async () => {
  return await act(async () => {
    await render(<Support />)
  })
}

describe('homepage: ProfileAndSupport: Support', () => {
  describe('render', () => {
    beforeEach(async () => {
      await renderSupport()
    })

    it('should display help links', async () => {
      const contactLink = await screen.findByText('Contacter le support', {
        selector: 'a',
      })
      const cguLink = await screen.findByText(
        'Conditions Générales d’Utilisation',
        {
          selector: 'a',
        }
      )
      const helpCenterLink = await screen.findByText('Centre d’aide', {
        selector: 'a',
      })

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
  })
})
