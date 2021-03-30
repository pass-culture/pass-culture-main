import '@testing-library/jest-dom'
import { screen } from '@testing-library/react'

import { renderOffer } from 'components/pages/Offers/Offer/Confirmation/__specs__/render'
import * as pcapi from 'repository/pcapi/pcapi'
import { offerFactory, stockFactory } from 'utils/apiFactories'
import { loadFakeApiOffer, loadFakeApiStocks } from 'utils/fakeApi'

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
      expect(screen.getByText('Confirmation')).toBeInTheDocument()
      expect(screen.getByText('Ajouter un stock', { selector: 'button' })).toBeInTheDocument()
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
  })
})

/*
  stocks
    creation (sans stocks)
      validation => confirmation
    édition (avec stocks)
      validation => pas confirmation
*/
