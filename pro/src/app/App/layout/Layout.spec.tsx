import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient//api'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Layout, LayoutProps } from './Layout'

const LABELS = {
  backToNavLink: /Revenir à la barre de navigation/,
}

type LayoutTestProps = Partial<LayoutProps> & {
  isConnected?: boolean
  isImpersonated?: boolean
}

const renderLayout = ({
  isImpersonated = false,
  isConnected = true,
  ...props
}: LayoutTestProps = {}) => {
  renderWithProviders(
    <Layout {...props} />,
    isConnected
      ? {
          user: sharedCurrentUserFactory({
            isImpersonated,
          }),
        }
      : {}
  )
}

describe('Layout', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      isValidated: true,
    })

    window.addEventListener = vi.fn()
    window.removeEventListener = vi.fn()
  })

  describe('side navigation', () => {
    describe('on smaller screen sizes', () => {
      beforeEach(() => {
        renderLayout()

        global.innerWidth = 500
        global.dispatchEvent(new Event('resize'))
      })

      it('should render the button menu', () => {
        expect(screen.getByLabelText('Menu')).toBeInTheDocument()
      })

      it('should focus the close button when the button menu is clicked', async () => {
        await userEvent.click(screen.getByLabelText('Menu'))

        expect(screen.getByLabelText('Fermer')).toHaveFocus()
      })

      it('should trap focus when side nav is open', async () => {
        await userEvent.click(screen.getByLabelText('Menu'))

        expect(screen.getByLabelText('Fermer')).toHaveFocus()
        const NB_ITEMS_IN_NAV = 11
        for (let i = 0; i < NB_ITEMS_IN_NAV; i++) {
          await userEvent.tab()
        }
        expect(screen.getByLabelText('Fermer')).toHaveFocus()
      })
    })
  })

  describe('about main heading & back to nav link', () => {
    it('should render a main heading when provided', () => {
      const mainHeading = 'Home'
      renderLayout({ mainHeading })

      expect(
        screen.getByRole('heading', { name: mainHeading })
      ).toBeInTheDocument()
    })

    it('should render a back to nav link when a main heading is provided and when user is connected', () => {
      renderLayout({ mainHeading: 'Home', isConnected: true })

      expect(
        screen.getByRole('link', { name: LABELS.backToNavLink })
      ).toBeInTheDocument()
    })

    it('should not render a back to nav link when not connected', () => {
      renderLayout({ mainHeading: 'Home', isConnected: false })

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

  it('should render sign up banners', () => {
    renderLayout({ layout: 'sign-up' })

    expect(screen.getByTestId('sign-up-header')).toBeInTheDocument()
    expect(screen.getByTestId('sign-up-logo')).toBeInTheDocument()
  })

  describe('showFooter', () => {
    it('should display footer by default', () => {
      renderLayout()

      expect(screen.getByTestId('app-footer')).toBeInTheDocument()
    })

    it('should not display footer is "showFooter" is false', () => {
      renderLayout({ isImpersonated: false, showFooter: false })

      expect(screen.queryByTestId('app-footer')).not.toBeInTheDocument()
    })

    it('should not display footer by default if layout is "funnel"', () => {
      renderLayout({ isImpersonated: false, layout: 'funnel' })

      expect(screen.queryByTestId('app-footer')).not.toBeInTheDocument()
    })
  })
})
