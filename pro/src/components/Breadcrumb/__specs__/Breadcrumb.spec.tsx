import { screen } from '@testing-library/react'

import { renderWithProviders } from 'utils/renderWithProviders'

import Breadcrumb, { Crumb } from '../Breadcrumb'

const crumbs: Crumb[] = [
  { title: 'Link 1', link: { to: './link1', isExternal: false } },
  {
    title: 'Link 2',
    link: { to: './link2', isExternal: false },
    icon: 'icon_url',
  },
  { title: 'Link 3', link: { to: './link3', isExternal: false } },
]

describe('Breadcrumb', () => {
  it('should display a navigation with a list of links', () => {
    renderWithProviders(<Breadcrumb crumbs={crumbs} />)

    expect(
      screen.getByRole('navigation', { name: "Fil d'ariane" })
    ).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Link 1' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Link 3' })).toBeInTheDocument()
  })

  it('should announce the last link as the current page for assistive technologies', () => {
    renderWithProviders(<Breadcrumb crumbs={crumbs} />)

    expect(screen.getByRole('link', { name: 'Link 2' })).not.toHaveAttribute(
      'aria-current',
      'page'
    )
    expect(screen.getByRole('link', { name: 'Link 3' })).toHaveAttribute(
      'aria-current',
      'page'
    )
  })
})
