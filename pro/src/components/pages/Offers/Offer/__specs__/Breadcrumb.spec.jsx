/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
*/

import '@testing-library/jest-dom'
import { screen } from '@testing-library/react'

import { renderOffer } from 'components/pages/Offers/Offer/__specs__/render'
import { offerFactory, offererFactory, venueFactory, stockFactory } from 'utils/apiFactories'
import {
  getFakeApiUserValidatedOfferersNames,
  getFakeApiVenuesForOfferer,
  loadFakeApiOffer,
  loadFakeApiStocks,
  loadFakeApiCategories,
  loadFakeApiVenue,
} from 'utils/fakeApi'
import { queryByTextTrimHtml } from 'utils/testHelpers'

describe('offer step', () => {
  describe('in creation mode', () => {
    it('should display breadcrumb without link', async () => {
      // Given
      const offerer = offererFactory()
      const venue = venueFactory()
      loadFakeApiCategories()
      getFakeApiUserValidatedOfferersNames(offerer)
      getFakeApiVenuesForOfferer(venue)

      // When
      await renderOffer({ pathname: '/offres/creation' })

      // Then
      const detailTab = await screen.findByText("Détails de l'offre")
      expect(detailTab).toBeInTheDocument()
      expect(detailTab).not.toHaveAttribute('href')
      expect(detailTab.closest('.bc-step')).toHaveClass('active')
      const stockTab = screen.getByText('Stock et prix')
      expect(stockTab).toBeInTheDocument()
      expect(stockTab).not.toHaveAttribute('href')
      const confirmationTab = screen.getByText('Confirmation')
      expect(confirmationTab).toBeInTheDocument()
      expect(confirmationTab).not.toHaveAttribute('href')
    })
  })

  describe('in edition mode', () => {
    it('should display breadcrumb whithout "Confirmation" tab', async () => {
      // Given
      const offer = offerFactory({ subcategoryId: 'LIVRE_PAPIER' })
      loadFakeApiOffer(offer)
      const venue = venueFactory()
      loadFakeApiVenue(venue)
      loadFakeApiCategories()

      // When
      await renderOffer({ pathname: `/offres/${offer.id}/edition` })

      // Then
      const detailTab = await screen.findByText("Détails de l'offre", { selector: 'a' })
      expect(detailTab).toBeInTheDocument()
      expect(detailTab.closest('.bc-step')).toHaveClass('active')
      expect(screen.getByText('Stock et prix', { selector: 'a' })).toBeInTheDocument()
      expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()
    })
  })
})

describe('stocks step', () => {
  describe('in creation mode', () => {
    it('should display breadcrumb without link', async () => {
      // Given
      const offer = offerFactory({ status: 'DRAFT', subcategoryId: 'LIVRE_PAPIER' })
      loadFakeApiOffer(offer)
      loadFakeApiStocks([])

      // When
      await renderOffer({ pathname: `/offres/${offer.id}/stocks` })

      // Then
      const detailTab = await screen.findByText("Détails de l'offre")
      expect(detailTab).toBeInTheDocument()
      expect(detailTab).not.toHaveAttribute('href')
      const stockTab = queryByTextTrimHtml(screen, 'Stock et prix', {
        selector: 'li',
        leafOnly: false,
      })
      expect(stockTab).toBeInTheDocument()
      expect(stockTab).not.toHaveAttribute('href')
      expect(stockTab).toHaveClass('active')
      const confirmationTab = screen.getByText('Confirmation')
      expect(confirmationTab).toBeInTheDocument()
      expect(confirmationTab).not.toHaveAttribute('href')
    })
  })

  describe('in edition mode', () => {
    it('should display breadcrumb without "Confirmation" tab', async () => {
      // Given
      const stock = stockFactory()
      const offer = offerFactory({ status: 'ACTIVE', subcategoryId: 'LIVRE_PAPIER' })
      loadFakeApiOffer(offer)
      loadFakeApiStocks([stock])

      // When
      await renderOffer({ pathname: `/offres/${offer.id}/stocks` })

      // Then
      const detailTab = await screen.findByText("Détails de l'offre", { selector: 'a' })
      expect(detailTab).toBeInTheDocument()
      const stockTab = screen.getByText('Stock et prix', { selector: 'a' })
      expect(stockTab).toBeInTheDocument()
      expect(stockTab.closest('.bc-step')).toHaveClass('active')
      expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()
    })
  })
})

describe('confirmation step', () => {
  describe('in creation mode', () => {
    it('should display breadcrumb without link', async () => {
      // Given
      const offer = offerFactory({
        name: 'mon offer',
        status: 'DRAFT',
        subcategoryId: 'LIVRE_PAPIER',
      })
      loadFakeApiOffer(offer)

      // When
      await renderOffer({ pathname: `/offres/${offer.id}/confirmation` })

      // Then
      const detailTab = await screen.findByText("Détails de l'offre")
      expect(detailTab).toBeInTheDocument()
      expect(detailTab).not.toHaveAttribute('href')
      const stockTab = screen.getByText('Stock et prix')
      expect(stockTab).toBeInTheDocument()
      expect(stockTab).not.toHaveAttribute('href')
      const confirmationTab = queryByTextTrimHtml(screen, 'Confirmation', {
        selector: 'li',
        leafOnly: false,
      })
      expect(confirmationTab).toBeInTheDocument()
      expect(confirmationTab).not.toHaveAttribute('href')
      expect(confirmationTab).toHaveClass('active')
    })
  })
})
