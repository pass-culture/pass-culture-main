import { screen } from '@testing-library/react'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { renderWithProviders } from 'commons/utils/renderWithProviders'
import strokeLibraryIcon from 'icons/stroke-library.svg'
import strokeUserIcon from 'icons/stroke-user.svg'

import { Tabs } from '../Tabs'

const renderTabs = (nav?: string) => {
  renderWithProviders(
    <Routes>
      <Route
        path="/offres"
        element={
          <Tabs
            selectedKey="individual"
            tabs={[
              {
                label: 'Offres individuelles',
                url: '/offres',
                key: 'individual',
                icon: strokeUserIcon,
              },
              {
                label: 'Offres collectives',
                url: '/offres/collectives',
                key: 'collective',
                icon: strokeLibraryIcon,
              },
            ]}
            nav={nav}
          />
        }
      />
    </Routes>,
    {
      initialRouterEntries: ['/offres'],
    }
  )
}

describe('src | components | Tabs', () => {
  it('should render tabs', () => {
    renderTabs()
    expect(
      screen.getByRole('tab', {
        name: 'Offres individuelles',
      })
    ).toHaveAttribute('href', '/offres')
    expect(screen.queryByRole('navigation')).not.toBeInTheDocument()
  })

  describe('Accessibility', () => {
    it('should render tabs as a navigation', () => {
      renderTabs('Offres individuelles et collectives')
      expect(screen.getByRole('navigation')).toHaveAttribute(
        'aria-label',
        'Offres individuelles et collectives'
      )
    })

    it('should indicate current page', () => {
      renderTabs('Offres individuelles et collectives')

      expect(
        screen.getByRole('tab', {
          name: 'Offres individuelles',
        })
      ).toHaveAttribute('aria-selected', 'true')

      expect(
        screen.getByRole('tab', {
          name: 'Offres individuelles',
        })
      ).toHaveAttribute('data-state', 'active')
    })

    it('should not indicate current page', () => {
      renderTabs('Offres individuelles et collectives')

      expect(
        screen.getByRole('tab', {
          name: 'Offres collectives',
        })
      ).not.toHaveAttribute('aria-selected', 'true')
    })
  })
})
