import '@testing-library/jest-dom'
import { fireEvent, screen } from '@testing-library/react'

import { renderOffer } from 'components/pages/Offers/Offer/Confirmation/__specs__/render'
import * as pcapi from 'repository/pcapi/pcapi'
import { offerFactory, stockFactory } from 'utils/apiFactories'
import { bulkFakeApiCreateOrEditStock, loadFakeApiOffer, loadFakeApiStocks } from 'utils/fakeApi'

describe('confirmation on stocks form', () => {
  afterEach(() => {
    jest.spyOn(pcapi, 'getUserValidatedOfferersNames').mockRestore()
    jest.spyOn(pcapi, 'getVenuesForOfferer').mockRestore()
    jest.spyOn(pcapi, 'loadStocks').mockRestore()
    jest.spyOn(pcapi, 'loadTypes').mockRestore()
  })

  describe('when creation mode', () => {
    it('should display "Confirmation" in the breadcrumb', async () => {
      // Given
      const offer = offerFactory({}, null)
      loadFakeApiOffer(offer)
      loadFakeApiStocks([])

      // When
      await renderOffer(`/offres/${offer.id}/stocks`)

      // Then
      const confirmationStep = screen.getByText('Confirmation')
      expect(confirmationStep).toBeInTheDocument()
      expect(confirmationStep).not.toHaveAttribute('href')
      expect(screen.getByText('Ajouter un stock', { selector: 'button' })).toBeInTheDocument()
    })

    it('should land on confirmation page after validating of stocks', async () => {
      // Given
      const offer = offerFactory({}, null)
      loadFakeApiOffer(offer)
      loadFakeApiStocks([])
      bulkFakeApiCreateOrEditStock({ id: 'MEFA' })
      await renderOffer(`/offres/${offer.id}/stocks`)
      fireEvent.click(screen.getByText('Ajouter un stock', { selector: 'button' }))

      // When
      fireEvent.click(screen.getByText('Enregistrer', { selector: 'button' }))

      // Then
      expect(await screen.findByText('Offre créée !')).toBeInTheDocument()
    })
  })

  describe('when edition mode with stocks', () => {
    it('should display "Confirmation" in the breadcrumb', async () => {
      // Given
      const stock = stockFactory()
      const offer = offerFactory()
      loadFakeApiOffer(offer)
      loadFakeApiStocks([stock])

      // When
      await renderOffer(`/offres/${offer.id}/stocks`)

      // Then
      expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()
      expect(screen.getByText('Enregistrer', { selector: 'button' })).toBeInTheDocument()
    })

    it('should not land on confirmation page after validating of stocks', async () => {
      // Given
      const stock = stockFactory()
      const offer = offerFactory()
      loadFakeApiOffer(offer)
      loadFakeApiStocks([stock])
      await renderOffer(`/offres/${offer.id}/stocks`)

      // When
      fireEvent.click(screen.getByText('Enregistrer', { selector: 'button' }))

      // Then
      expect(screen.queryByText('Offre créée !')).not.toBeInTheDocument()
    })
  })
})
