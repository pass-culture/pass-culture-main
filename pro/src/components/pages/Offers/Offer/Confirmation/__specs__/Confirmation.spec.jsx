import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'

import { api } from 'apiClient/api'
import { renderOffer } from 'components/pages/Offers/Offer/__specs__/render'
import { offerFactory } from 'utils/apiFactories'

jest.mock('utils/config', () => {
  return {
    WEBAPP_URL: 'http://localhost',
  }
})

describe('confirmation page', () => {
  it('should display the rights information when offer is not pending', async () => {
    // Given
    const offer = offerFactory({
      name: 'mon offre',
      status: 'DRAFT',
      venueId: 'VENUEID',
    })
    jest.spyOn(api, 'getOffer').mockResolvedValue(offer)

    // When
    await renderOffer({
      pathname: `/offre/${offer.id}/individuel/creation/confirmation`,
    })

    // Then
    expect(screen.queryByText('active')).not.toBeInTheDocument()
    expect(
      screen.getByText('Offre publiée !', { selector: 'h2' })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Votre offre est désormais disponible à la réservation sur l’application pass Culture.',
        { selector: 'p' }
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
      })
    ).toHaveAttribute('href', `http://localhost/offre/${offer.nonHumanizedId}`)
    expect(
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute(
      'href',
      `/offre/creation/individuel?structure=${offer.venue.managingOffererId}&lieu=${offer.venueId}`
    )
    expect(
      screen.getByText('Voir la liste des offres', { selector: 'a' })
    ).toHaveAttribute('href', `/offres`)
  })

  it('should display the rights information when offer is pending', async () => {
    // Given
    const offer = offerFactory({
      name: 'mon offre',
      status: 'PENDING',
      venueId: 'VENUEID',
    })
    jest.spyOn(api, 'getOffer').mockResolvedValue(offer)

    // When
    await renderOffer({
      pathname: `/offre/${offer.id}/individuel/creation/confirmation`,
    })

    // Then
    expect(screen.queryByText('active')).not.toBeInTheDocument()
    expect(
      screen.getByText('Offre en cours de validation', { selector: 'h2' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText(content =>
        content.startsWith(
          'Votre offre est en cours de validation par l’équipe pass Culture'
        )
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText('Visualiser l’offre dans l’application', {
        selector: 'a',
      })
    ).toHaveAttribute('href', `http://localhost/offre/${offer.nonHumanizedId}`)
    expect(
      screen.getByText('Créer une nouvelle offre', { selector: 'a' })
    ).toHaveAttribute(
      'href',
      `/offre/creation/individuel?structure=${offer.venue.managingOffererId}&lieu=${offer.venueId}`
    )
    expect(
      screen.getByText('Voir la liste des offres', { selector: 'a' })
    ).toHaveAttribute('href', `/offres`)
  })
})
