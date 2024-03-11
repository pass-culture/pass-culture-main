import { screen } from '@testing-library/react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { Sitemap } from '../Sitemap'

const renderSitemap = () => {
  return renderWithProviders(<Sitemap />)
}

describe('Sitemap', () => {
  it('should render the sitemap', () => {
    renderSitemap()
    expect(
      screen.getByRole('heading', { name: 'Plan du site' })
    ).toBeInTheDocument()
  })
})
