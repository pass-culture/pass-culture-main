import '@testing-library/jest-dom'
import { screen } from '@testing-library/react'

import { renderOffer } from 'components/pages/Offers/Offer/__specs__/render'
import { offerFactory } from 'utils/apiFactories'
import { loadFakeApiOffer } from 'utils/fakeApi'

describe('confirmation page', () => {
  it('should display the rights information', async () => {
    // Given
    const offer = offerFactory({ status: 'DRAFT' })
    loadFakeApiOffer(offer)

    // When
    await renderOffer(`/offres/${offer.id}/confirmation`)

    // Then
    expect(screen.queryByText('active')).not.toBeInTheDocument()
    expect(screen.getByText('Offre créée !', { selector: 'h2' })).toBeInTheDocument()
    expect(
      screen.getByText(
        'Votre offre est désormais disponible à la réservation sur l’application pass Culture.',
        { selector: 'p' }
      )
    ).toBeInTheDocument()
    expect(screen.getByText('Prévisualiser dans l’app', { selector: 'a' })).toHaveAttribute(
      'href',
      `http://localhost/offre/details/${offer.id}`
    )
    expect(screen.getByText('Créer une nouvelle offre', { selector: 'a' })).toHaveAttribute(
      'href',
      '/offres/creation'
    )
  })

  it('should redirect to edition when the offer is not a draft', async () => {
    // Given
    const offer = offerFactory({ status: 'ACTIVE' })
    loadFakeApiOffer(offer)

    // When
    await renderOffer([`/offres/${offer.id}/edition`, `/offres/${offer.id}/confirmation`])

    // Then
    expect(screen.getByText('Éditer une offre')).toBeInTheDocument()
  })
})
