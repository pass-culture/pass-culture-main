import { screen } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { FunnelLayout, type FunnelLayoutProps } from './FunnelLayout'

const LABELS = {
  backToNavLink: /Revenir à la barre de navigation/,
}

type FunnelLayoutTestProps = Partial<FunnelLayoutProps> & {
  isConnected?: boolean
  isImpersonated?: boolean
}

const renderLayout = ({
  isImpersonated,
  isConnected,
  withFlexContent,
  ...props
}: FunnelLayoutTestProps = {}) => {
  renderWithProviders(
    <FunnelLayout
      {...props}
      mainHeading="Votre structure"
      withFlexContent={withFlexContent}
    />,
    isConnected
      ? {
          user: sharedCurrentUserFactory({
            isImpersonated,
          }),
        }
      : {}
  )
}

describe('FunnelLayout', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      isValidated: true,
    })

    window.addEventListener = vi.fn()
    window.removeEventListener = vi.fn()
  })

  it('should always render a main landmark and a heading level 1', () => {
    renderLayout({ isConnected: true })

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
  })

  describe('about main heading & back to nav link', () => {
    it('should not render a back to nav link when not connected', () => {
      renderLayout({ isConnected: false })

      expect(
        screen.queryByRole('link', { name: LABELS.backToNavLink })
      ).not.toBeInTheDocument()
    })
  })

  it('should render connect as banner if user has isImpersonated value is true', () => {
    renderLayout({ isConnected: true, isImpersonated: true })

    expect(
      screen.getByText('Vous êtes connecté en tant que :')
    ).toBeInTheDocument()
  })

  describe('showFooter', () => {
    it('should not display footer by default', () => {
      renderLayout({ isConnected: true, isImpersonated: false })

      expect(screen.queryByTestId('app-footer')).not.toBeInTheDocument()
    })
  })

  it('should render main content with default class when withFlexContent is false', () => {
    renderLayout({ isConnected: true })

    const main = screen.getByRole('main')
    expect(main.className).toBe('content')
  })

  it('should render main content with flex class when withFlexContent is true', () => {
    renderLayout({ isConnected: true, withFlexContent: true })

    const main = screen.getByRole('main')
    expect(main.className).toBe('content-flex')
  })
})
