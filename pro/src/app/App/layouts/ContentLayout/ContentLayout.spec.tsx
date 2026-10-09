import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { ContentLayout } from '@/app/App/layouts/ContentLayout/ContentLayout'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SkipLinksProvider } from '@/components/SkipLinks/SkipLinksContext'

vi.mock('@/commons/hooks/useMediaQuery', async (importOriginal) => ({
  ...(await importOriginal()),
  useMediaQuery: vi.fn(),
}))

const renderContentLayout = (options: RenderWithProvidersOptions = {}) =>
  renderWithProviders(
    <SkipLinksProvider>
      <ContentLayout>Full Layout Content</ContentLayout>
    </SkipLinksProvider>,
    {
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
        },
      },
      ...options,
    }
  )

describe('<ContentLayout />', () => {
  beforeEach(() => {
    vi.spyOn(window, 'addEventListener').mockImplementation(() => {})
    vi.spyOn(window, 'removeEventListener').mockImplementation(() => {})
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderContentLayout()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render children inside the main landmark', () => {
    renderContentLayout()

    expect(screen.getByRole('main')).toHaveTextContent('Full Layout Content')
  })

  it('should not render the "connected as" aside for a regular user', () => {
    renderContentLayout()

    expect(
      screen.queryByRole('complementary', { name: 'Connect as' })
    ).not.toBeInTheDocument()
  })

  it('should render the "connected as" aside when the user is impersonated', () => {
    renderContentLayout({
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory({
            isImpersonated: true,
            firstName: 'John',
            lastName: 'Doe',
          }),
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
        },
      },
    })

    expect(
      screen.getByRole('complementary', { name: 'Connect as' })
    ).toHaveTextContent('John Doe')
  })

  describe('lateral panel / side navigation on smaller screen sizes', () => {
    beforeEach(() => {
      vi.mocked(useMediaQuery).mockReturnValue(false)
      renderContentLayout()
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

      await userEvent.tab()

      expect(
        document
          .getElementById('lateral-panel')
          ?.contains(document.activeElement)
      ).toBe(true)
    })
  })

  it('should portal "go to menu" skip link when SkipLinks context provides a container', () => {
    renderContentLayout()

    expect(
      screen.getByRole('link', { name: 'Aller au menu' })
    ).toBeInTheDocument()
  })

  it('should point the "go to menu" skip link to #lateral-panel on small screens', () => {
    vi.mocked(useMediaQuery).mockReturnValue(false)
    renderContentLayout()

    expect(screen.getByRole('link', { name: 'Aller au menu' })).toHaveAttribute(
      'href',
      '#lateral-panel'
    )
  })

  it('should point the "go to menu" skip link to #header-nav-toggle on laptop screens', () => {
    vi.mocked(useMediaQuery).mockReturnValue(true)
    renderContentLayout()

    expect(screen.getByRole('link', { name: 'Aller au menu' })).toHaveAttribute(
      'href',
      '#header-nav-toggle'
    )
  })
})
