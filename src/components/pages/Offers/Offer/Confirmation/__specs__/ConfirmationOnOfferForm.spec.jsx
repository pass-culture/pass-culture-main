import '@testing-library/jest-dom'
import { screen } from '@testing-library/react'

import { renderOffer } from 'components/pages/Offers/Offer/Confirmation/__specs__/render'
import * as pcapi from 'repository/pcapi/pcapi'
import { offerFactory, offererFactory, venueFactory } from 'utils/apiFactories'
import {
  getFakeApiUserValidatedOfferersNames,
  getFakeApiVenuesForOfferer,
  loadFakeApiOffer,
  loadFakeApiTypes,
} from 'utils/fakeApi'

describe('confirmation on offer form', () => {
  afterEach(() => {
    jest.spyOn(pcapi, 'getUserValidatedOfferersNames').mockRestore()
    jest.spyOn(pcapi, 'getVenuesForOfferer').mockRestore()
    jest.spyOn(pcapi, 'loadStocks').mockRestore()
    jest.spyOn(pcapi, 'loadTypes').mockRestore()
  })

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
      expect(screen.getByText('Confirmation')).toBeInTheDocument()
      expect(await screen.findByText("Type d'offre")).toBeInTheDocument()
    })
  })

  describe('when edition mode', () => {
    it('should display "Confirmation" in the breadcrumb', async () => {
      // Given
      const offer = offerFactory({}, null)
      loadFakeApiOffer(offer)
      loadFakeApiTypes()

      // When
      await renderOffer(`/offres/${offer.id}/edition`)

      // Then
      expect(screen.getByText('Confirmation')).toBeInTheDocument()
      expect(await screen.findByText("Type d'offre")).toBeInTheDocument()
    })
  })

  describe('when edition mode with stocks', () => {
    it('should display "Confirmation" in the breadcrumb', async () => {
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
