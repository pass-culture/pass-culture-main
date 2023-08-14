import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import CookiesFooter from '../CookiesFooter'

const overrideStore = {
  features: {
    initialized: true,
    list: [
      {
        isActive: true,
        nameKey: 'WIP_ENABLE_COOKIES_BANNER',
      },
    ],
  },
}

const renderCookiesFooter = () => {
  renderWithProviders(<CookiesFooter />, { storeOverrides: overrideStore })
}

describe('CookiesFooter', () => {
  it('should render cookies footer links', async () => {
    renderCookiesFooter()

    expect(screen.getByText(/CGU professionnels/)).toBeInTheDocument()
    expect(
      screen.getByText(/Charte des Données Personnelles/)
    ).toBeInTheDocument()
    expect(screen.getByText(/Gestion des cookies/)).toBeInTheDocument()
  })
})
