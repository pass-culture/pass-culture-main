import { render, screen } from '@testing-library/react'

import { Tabs } from './Tabs'

vi.mock('./TabItems/TabItems', () => ({
  TabItems: vi.fn(() => <div>Mocked TabItems</div>),
}))

vi.mock('./NavLinkItems/NavLinkItems', () => ({
  NavLinkItems: vi.fn(() => <div>Mocked NavLinkItems</div>),
}))

describe('Tabs', () => {
  it('should render NavLinkItems when given type="links"', () => {
    render(
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
        navLabel={'Tabs - links mode'}
      />
    )

    expect(screen.queryByText(/NavLinkItems/)).toBeInTheDocument()
    expect(screen.queryByText(/TabItems/)).not.toBeInTheDocument()
  })

  it('should render TabItems when given type="tabs"', () => {
    render(
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
        onChange={vi.fn()}
        navLabel={'Tabs - tabs mode'}
      />
    )

    expect(screen.queryByText(/TabItems/)).toBeInTheDocument()
    expect(screen.queryByText(/NavLinkItems/)).not.toBeInTheDocument()
  })
})
