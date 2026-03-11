import { screen } from '@testing-library/react'
import { createRef } from 'react'
import { Route, Routes } from 'react-router'

import { LateralPanel } from '@/app/App/layouts/BasicLayout/LateralPanel/LateralPanel'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Footer } from '@/components/Footer/Footer'
import { SkipLinksProvider } from '@/components/SkipLinks/SkipLinksContext'

import { SkipLinks } from '../SkipLinks'

vi.mock('@/commons/hooks/useMediaQuery', async (importOriginal) => ({
  ...(await importOriginal()),
  useMediaQuery: vi.fn(),
}))

const renderApp = ({
  withLateralPanel = false,
  withFooter = false,
}: {
  withLateralPanel?: boolean
  withFooter?: boolean
} = {}) =>
  renderWithProviders(
    <Routes>
      <Route
        element={
          <SkipLinksProvider>
            <SkipLinks />
            {withLateralPanel && (
              <LateralPanel
                isOpen={false}
                onToggle={vi.fn()}
                openButtonRef={createRef()}
                closeButtonRef={createRef()}
                navPanel={createRef()}
              />
            )}
            <div id="content">
              <a href="#">focusable content element</a>
            </div>
            {withFooter && <Footer />}
          </SkipLinksProvider>
        }
        path="/accueil"
      />
    </Routes>,
    { initialRouterEntries: ['/accueil'] }
  )

describe('SkipLinks', () => {
  it('should render', () => {
    renderApp()
    expect(screen.queryByText('Aller au contenu')).toBeInTheDocument()
    expect(screen.queryByText('Menu')).not.toBeInTheDocument()
  })

  it('should always render the "go to content" skip link', () => {
    renderApp()

    expect(
      screen.getByRole('link', { name: 'Aller au contenu' })
    ).toBeInTheDocument()
  })

  it('should render the "go to menu" skip link when LateralPanel is in the tree', () => {
    renderApp({ withLateralPanel: true })

    expect(
      screen.getByRole('link', { name: 'Aller au menu' })
    ).toBeInTheDocument()
  })

  it('should not render the "go to menu" skip link without LateralPanel', () => {
    renderApp()

    expect(
      screen.queryByRole('link', { name: 'Aller au menu' })
    ).not.toBeInTheDocument()
  })

  it('should render the "go to footer" skip link when Footer is in the tree', () => {
    renderApp({ withFooter: true })

    expect(
      screen.getByRole('link', { name: 'Aller au pied de page' })
    ).toBeInTheDocument()
  })

  it('should not render the "go to footer" skip link without Footer', () => {
    renderApp()

    expect(
      screen.queryByRole('link', { name: 'Aller au pied de page' })
    ).not.toBeInTheDocument()
  })
})
