import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Link, Route, Routes } from 'react-router'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { PageTitleAnnouncer } from '@/components/PageTitleAnnouncer/PageTitleAnnouncer'

import { usePageTitle } from '../usePageTitle'

const PageTitle = (): null => {
  usePageTitle()
  return null
}

const renderusePageTitleRoutes = (url = '/accueil') => {
  renderWithProviders(
    <>
      <Routes>
        <Route
          path="/accueil"
          element={
            <>
              <PageTitle />
              <span>Main page</span>
              <Link to="/guichet">Guichet</Link>
            </>
          }
        />
        <Route
          path="/guichet"
          element={
            <>
              <PageTitle />
              <span>Guichet page</span>
            </>
          }
        />
        <Route
          path="/inscription/structure/recherche"
          element={
            <>
              <PageTitle />
              <span>Structure page</span>
            </>
          }
        />
      </Routes>
      <PageTitleAnnouncer />
    </>,
    { initialRouterEntries: [url] }
  )
}

describe('usePageTitle', () => {
  it('should set initial page title', () => {
    renderusePageTitleRoutes()
    expect(document.title).toEqual(
      'Espace acteurs culturels - pass Culture Pro'
    )
  })

  it('should update page title when user navigates to another page', async () => {
    renderusePageTitleRoutes()
    await userEvent.click(screen.getByRole('link', { name: 'Guichet' }))
    expect(document.title).toEqual('Guichet - pass Culture Pro')
  })

  it('should update aria pane name announcer region when user navigates to another page', async () => {
    renderusePageTitleRoutes()
    await userEvent.click(screen.getByRole('link', { name: 'Guichet' }))
    const pageTitleAnnouncer = screen.getByTestId('page-title-announcer')
    expect(pageTitleAnnouncer).toHaveTextContent('Guichet')
  })
})
