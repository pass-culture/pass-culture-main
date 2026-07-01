import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { WarningObsoleteNavigator } from './WarningObsoleteNavigator'

const originalUserAgent = window.navigator.userAgent

const setUserAgent = (userAgent: string) => {
  Object.defineProperty(window.navigator, 'userAgent', {
    configurable: true,
    value: userAgent,
  })
}

describe('WarningObsoleteNavigator', () => {
  afterEach(() => {
    setUserAgent(originalUserAgent)
  })

  describe('component rendering', () => {
    it('should render nothing for supported browser', () => {
      setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
      )

      const { container } = renderWithProviders(<WarningObsoleteNavigator />)

      expect(container).toBeEmptyDOMElement()
    })

    it('should render nothing for unknown browser', () => {
      setUserAgent(
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.78.94 Safari/537.36'
      )

      renderWithProviders(<WarningObsoleteNavigator />)

      expect(
        screen.getByText('Votre navigateur est obsolète')
      ).toBeInTheDocument()
    })

    it('should render warning banner for obsolete browser', () => {
      setUserAgent(
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15'
      )

      renderWithProviders(<WarningObsoleteNavigator />)

      expect(
        screen.getByText('Votre navigateur est obsolète')
      ).toBeInTheDocument()
    })
  })
})
