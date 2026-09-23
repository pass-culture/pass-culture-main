import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component } from './NonAttached'

describe('NonAttachedBanner', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<Component />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render the onboarding heading', () => {
    renderWithProviders(<Component />)

    expect(
      screen.getByRole('heading', {
        name: 'Bienvenue sur votre espace partenaire',
      })
    ).toBeInTheDocument()
  })
})
