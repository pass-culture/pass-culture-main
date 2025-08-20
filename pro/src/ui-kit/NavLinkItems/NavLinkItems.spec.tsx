import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { NavLinkItems } from './NavLinkItems'

const renderNavLinkItems = (nav: string = 'Menu') => {
  return renderWithProviders(
    <Routes>
      <Route
        path="/offres"
        element={
          <NavLinkItems
            selectedKey="individual"
            links={[
              {
                label: 'Offres individuelles',
                url: '/offres',
                key: 'individual',
              },
              {
                label: 'Offres collectives',
                url: '/offres/collectives',
                key: 'collective',
              },
            ]}
            navLabel={nav}
          />
        }
      />
    </Routes>,
    {
      initialRouterEntries: ['/offres'],
    }
  )
}

describe('NavLinkItems', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderNavLinkItems()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render links', () => {
    renderNavLinkItems()
    expect(
      screen.getByRole('link', {
        name: 'Lien actif Offres individuelles',
      })
    ).toHaveAttribute('href', '/offres')
  })
})
