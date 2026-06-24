import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SynchronizedBanner } from './SynchronizedBanner'

describe('IndividualOffer::SynchronizedBanner', () => {
  it('should display synchronization information with provider name', () => {
    renderWithProviders(<SynchronizedBanner providerName="Allocine" />)

    expect(
      screen.getByText('Cette offre est synchronisée avec Allocine')
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Certaines informations ne peuvent pas être modifiées depuis votre espace partenaire.'
      )
    ).toBeInTheDocument()
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })

  it('should display a fallback provider name when provider is missing', () => {
    renderWithProviders(<SynchronizedBanner />)

    expect(
      screen.getByText(
        'Cette offre est synchronisée avec un fournisseur inconnu'
      )
    ).toBeInTheDocument()
  })
})
