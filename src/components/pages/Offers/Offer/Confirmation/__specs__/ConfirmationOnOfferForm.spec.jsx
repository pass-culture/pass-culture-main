import '@testing-library/jest-dom'
import { screen } from '@testing-library/react'

import { renderOffer } from 'components/pages/Offers/Offer/Confirmation/__specs__/render'
import { offerFactory, offererFactory, venueFactory } from 'utils/apiFactories'
import {
  getFakeApiUserValidatedOfferersNames,
  getFakeApiVenuesForOfferer,
  loadFakeApiOffer,
  loadFakeApiTypes,
} from 'utils/fakeApi'

describe('confirmation on offer form', () => {
  describe('when creation mode', () => {
    it('should display "Confirmation" in the breadcrumb', async () => {
      // Given
      const offerer = offererFactory()
      const venue = venueFactory()
      loadFakeApiTypes()
      getFakeApiUserValidatedOfferersNames(offerer)
      getFakeApiVenuesForOfferer(venue)

      // When
      await renderOffer('/offres/creation')

      // Then
      const confirmationStep = screen.getByText('Confirmation')
      expect(confirmationStep).toBeInTheDocument()
      expect(confirmationStep).not.toHaveAttribute('href')
      expect(await screen.findByText("Type d'offre")).toBeInTheDocument()
    })
  })

  describe('when edition mode', () => {
    it('should not display "Confirmation" in the breadcrumb', async () => {
      // Given
      const offer = offerFactory()
      loadFakeApiOffer(offer)
      loadFakeApiTypes()

      // When
      await renderOffer(`/offres/${offer.id}/edition`)

      // Then
      expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()
      expect(await screen.findByText("Type d'offre")).toBeInTheDocument()
    })
  })
})
