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
  isImpersonated = false,
  isConnected = true,
  withFlexContent = false,
  ...props
}: FunnelLayoutTestProps = {}) => {
  renderWithProviders(
    <FunnelLayout
      {...props}
      mainHeading="Votre structure"
      withFlexContent={withFlexContent}
      withVerticalScroll
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
    renderLayout()

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
    renderLayout({ isImpersonated: true })

    expect(
      screen.getByText('Vous êtes connecté en tant que :')
    ).toBeInTheDocument()
  })

  describe('showFooter', () => {
    it('should not display footer by default', () => {
      renderLayout({ isImpersonated: false })

      expect(screen.queryByTestId('app-footer')).not.toBeInTheDocument()
    })
  })

  it('should render main content with default class when withFlexContent is false', () => {
    renderLayout({ withFlexContent: false })

    const main = screen.getByRole('main')
    expect(main.className).toBe('content')
  })

  it('should render main content with flex class when withFlexContent is true', () => {
    renderLayout({ withFlexContent: true })

    const main = screen.getByRole('main')
    expect(main.className).toBe('content-flex')
  })
})
