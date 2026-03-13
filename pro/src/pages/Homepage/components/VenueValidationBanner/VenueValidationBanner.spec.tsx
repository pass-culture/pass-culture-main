import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { VenueValidationBanner } from './VenueValidationBanner'

describe('VenueValidationBanner', () => {
  it('should render the banner with the correct title, description and faq link', () => {
    renderWithProviders(<VenueValidationBanner />)

    expect(
      screen.getByText(
        'Votre structure est en cours de traitement par les équipes du pass Culture'
      )
    ).toBeVisible()
    expect(
      screen.getByText(
        'Vos offres seront publiées sous réserve de validation de votre structure.'
      )
    ).toBeVisible()

    const faqLink = screen.getByRole('link', {
      name: /En savoir plus sur le fonctionnement du pass Culture/,
    })
    expect(faqLink).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/4514252662172--Acteurs-Culturels-S-inscrire-et-comprendre-le-fonctionnement-du-pass-Culture-cr%C3%A9ation-d-offres-gestion-des-r%C3%A9servations-remboursements-etc-'
    )
  })
})
