import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SkipLinksProvider } from '@/components/SkipLinks/SkipLinksContext'

import { BasicLayout } from './BasicLayout'

vi.mock('@/commons/hooks/useMediaQuery', async (importOriginal) => ({
  ...(await importOriginal()),
  useMediaQuery: vi.fn(),
}))

const renderBasicLayout = () => {
  renderWithProviders(
    <SkipLinksProvider>
      <BasicLayout mainHeading="Titre" />
    </SkipLinksProvider>
  )
}

describe('BasicLayout', () => {
  beforeEach(() => {
    window.addEventListener = vi.fn()
    window.removeEventListener = vi.fn()
  })

  it('should always render a main landmark and a heading level 1', () => {
    renderBasicLayout()

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
  })

  describe('lateral panel / side navigation', () => {
    describe('on smaller screen sizes', () => {
      beforeEach(() => {
        renderBasicLayout()

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

  it('should portal "go to menu" skip link when SkipLinks context provides a container', () => {
    renderBasicLayout()

    expect(
      screen.getByRole('link', { name: 'Aller au menu' })
    ).toBeInTheDocument()
  })

  it('should point the "go to menu" skip link to #lateral-panel on small screens', () => {
    vi.mocked(useMediaQuery).mockReturnValue(false)
    renderBasicLayout()

    expect(screen.getByRole('link', { name: 'Aller au menu' })).toHaveAttribute(
      'href',
      '#lateral-panel'
    )
  })

  it('should point the "go to menu" skip link to #header-nav-toggle on laptop screens', () => {
    vi.mocked(useMediaQuery).mockReturnValue(true)
    renderBasicLayout()

    expect(screen.getByRole('link', { name: 'Aller au menu' })).toHaveAttribute(
      'href',
      '#header-nav-toggle'
    )
  })
})
