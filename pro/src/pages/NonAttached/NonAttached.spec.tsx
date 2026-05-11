import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component } from './NonAttached'

describe('NonAttachedBanner', () => {
  it('should render the onboarding heading', () => {
    renderWithProviders(<Component />)

    expect(
      screen.getByRole('heading', {
        name: 'Bienvenue sur votre espace partenaire',
      })
    ).toBeInTheDocument()
  })
})
