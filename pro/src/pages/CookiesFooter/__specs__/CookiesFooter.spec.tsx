import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CookiesFooter } from '../CookiesFooter'

const renderCookiesFooter = () => {
  renderWithProviders(<CookiesFooter />)
}

describe('CookiesFooter', () => {
  it('should render cookies footer links', () => {
    renderCookiesFooter()

    expect(screen.getByText(/CGU professionnels/)).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Accessibilité : non conforme' })
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Charte des Données Personnelles/)
    ).toBeInTheDocument()
    expect(screen.getByText(/Gestion des cookies/)).toBeInTheDocument()
  })
})
