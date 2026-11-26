import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { createMemoryRouter, RouterProvider } from 'react-router'

import { Tabs } from './Tabs'

const linkItems = [
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
]

const renderLinkTabs = () => {
  const router = createMemoryRouter(
    [
      {
        path: '*',
        element: (
          <Tabs
            selectedKey="individual"
            items={linkItems}
            navLabel={'Tabs - links mode'}
          />
        ),
      },
    ],
    { initialEntries: ['/offres'] }
  )
  render(<RouterProvider router={router} />)
  return router
}

describe('Tabs', () => {
  it('should render tabs with URL property as links', () => {
    renderLinkTabs()

    expect(
      screen.getByRole('tab', { name: /Offres individuelles/ })
    ).toHaveAttribute('href', '/offres')
    expect(
      screen.getByRole('tab', { name: /Offres collectives/ })
    ).toHaveAttribute('href', '/offres/collectives')
  })

  it('should navigate to the next tab url with the keyboard', async () => {
    const router = renderLinkTabs()

    screen.getByRole('tab', { name: /Offres individuelles/ }).focus()
    await userEvent.keyboard('{ArrowRight}')

    expect(router.state.location.pathname).toBe('/offres/collectives')
    expect(
      screen.getByRole('tab', { name: /Offres collectives/ })
    ).toHaveFocus()
  })

  it('should render tabs with button behavior (no URL)', async () => {
    const onClick = vi.fn()
    render(
      <Tabs
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
        onClick={onClick}
        navLabel={'Tabs - tabs mode'}
      />
    )

    expect(
      screen.getByRole('tab', { name: /Individuelles/ })
    ).toBeInTheDocument()

    await userEvent.click(screen.getByRole('tab', { name: /Collectives/ }))
    expect(onClick).toHaveBeenCalledWith('collective')
  })
})
