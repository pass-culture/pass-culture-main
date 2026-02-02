import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Tabs } from './Tabs'

const renderNavLinkItems = (nav: string = 'Menu') => {
  return renderWithProviders(
    <Routes>
      <Route
        path="/offres"
        element={
          <Tabs
            type="links"
            selectedKey="individual"
            items={[
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

const renderTabItems = (handleChange = () => {}) =>
  render(
    <div>
      <Tabs
        type="tabs"
        selectedKey="individual"
        items={[
          {
            label: 'Individuelles',
            key: 'individual',
          },
          {
            label: 'Collectives',
            key: 'collective',
          },
        ]}
        onChange={handleChange}
        navLabel={'Onglets - tabs mode'}
      />
      <div id="panel-individual" role="tabpanel"></div>
      <div id="panel-collective" role="tabpanel"></div>
    </div>
  )

describe('Tabs', () => {
  describe('[type="links"]', () => {
    it('should render without accessibility violations', async () => {
      const { container } = renderNavLinkItems()

      expect(await axe(container)).toHaveNoViolations()
    })

    it('should render links', () => {
      renderNavLinkItems()
      expect(
        screen.getByRole('link', {
          name: /Offres individuelles/,
        })
      ).toHaveAttribute('href', '/offres')
    })
  })

  describe('[type="tabs"]', () => {
    it('should render without accessibility violation', async () => {
      const { container } = renderTabItems()

      expect(await axe(container)).toHaveNoViolations()
    })

    it('should render two tabs', () => {
      renderTabItems()

      expect(screen.getAllByRole('tab')).toHaveLength(2)
      expect(screen.getByRole('tab', { selected: true })).toHaveTextContent(
        'Individuelles'
      )
      expect(screen.getByRole('tab', { selected: false })).toHaveTextContent(
        'Collectives'
      )
    })

    it('should have working tabs', async () => {
      const user = userEvent.setup()
      const handleClickMock = vi.fn()
      renderTabItems(handleClickMock)

      expect(screen.getByRole('tab', { selected: true })).toHaveTextContent(
        'Individuelles'
      )

      await user.click(screen.getByRole('tab', { name: /Collectives/ }))
      expect(handleClickMock).toHaveBeenCalledWith('collective')
    })
  })
})
