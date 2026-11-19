import { render, screen } from '@testing-library/react'

import { Tabs } from './Tabs'

describe('Tabs', () => {
  it('should render tabs with URL property', () => {
    render(
      <Tabs
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
        onClick={vi.fn()}
        navLabel={'Tabs - links mode'}
      />
    )

    expect(
      screen.getByRole('tab', { name: /Offres individuelles/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('tab', { name: /Offres collectives/ })
    ).toBeInTheDocument()
  })

  it('should render tabs with button behavior (no URL)', () => {
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
        onClick={vi.fn()}
        navLabel={'Tabs - tabs mode'}
      />
    )

    expect(
      screen.getByRole('tab', { name: /Individuelles/ })
    ).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: /Collectives/ })).toBeInTheDocument()
  })
})
