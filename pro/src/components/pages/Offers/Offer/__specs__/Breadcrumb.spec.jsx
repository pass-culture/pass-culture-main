import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'

import { api } from 'apiClient/api'
import { renderOffer } from 'components/pages/Offers/Offer/__specs__/render'
import {
  offerFactory,
  offererFactory,
  stockFactory,
  venueFactory,
} from 'utils/apiFactories'
import {
  getFakeApiUserValidatedOfferersNames,
  getFakeApiVenuesForOfferer,
  loadFakeApiCategories,
  loadFakeApiStocks,
  loadFakeApiVenue,
} from 'utils/fakeApi'

describe('individual offer step', () => {
  describe('in creation mode', () => {
    it('should display breadcrumb without link', async () => {
      // Given
      const offerer = offererFactory()
      const venue = venueFactory()
      loadFakeApiCategories()
      getFakeApiUserValidatedOfferersNames(offerer)
      getFakeApiVenuesForOfferer(venue)

      // When
      await renderOffer({ pathname: '/offre/creation/individuel' })

      // Then
      expect(await screen.getByTestId('stepper')).toBeInTheDocument()
      const detailTab = await screen.findByText("Détails de l'offre")
      expect(detailTab).toBeInTheDocument()
      expect(detailTab).not.toHaveAttribute('href')
      expect(detailTab.closest('li')).toHaveClass('active')
      const stockTab = screen.getByText('Stocks et prix')
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
      jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
      const venue = venueFactory()
      loadFakeApiVenue(venue)
      loadFakeApiCategories()

      // When
      await renderOffer({ pathname: `/offre/${offer.id}/individuel/edition` })

      // Then
      expect(await screen.getByTestId('bc-tab')).toBeInTheDocument()
      const detailTab = await screen.findByText("Détails de l'offre", {
        selector: 'a',
      })
      expect(detailTab).toBeInTheDocument()
      expect(detailTab.closest('.bc-step')).toHaveClass('active')
      expect(
        screen.getByText('Stocks et prix', { selector: 'a' })
      ).toBeInTheDocument()
      expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()
    })
  })
})

describe('stocks step', () => {
  describe('in creation mode', () => {
    it('should display breadcrumb with link', async () => {
      // Given
      const offer = offerFactory({
        status: 'DRAFT',
        subcategoryId: 'LIVRE_PAPIER',
      })
      jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
      loadFakeApiStocks([])

      // When
      await renderOffer({
        pathname: `/offre/${offer.id}/individuel/creation/stocks`,
      })

      // Then
      expect(await screen.getByTestId('stepper')).toBeInTheDocument()
      const detailTab = await screen
        .getByText("Détails de l'offre")
        .closest('a')
      expect(detailTab).toBeInTheDocument()
      expect(detailTab).toHaveAttribute('href')
      const stockTab = await screen
        .getByText('Stocks et prix', { selector: 'span' })
        .closest('a')
      expect(stockTab).toBeInTheDocument()
      expect(stockTab).toHaveAttribute('href')
      expect(stockTab.closest('li')).toHaveClass('active')
      const confirmationTab = screen.getByText('Confirmation')
      expect(confirmationTab).toBeInTheDocument()
      expect(confirmationTab).not.toHaveAttribute('href')
    })
  })

  describe('in edition mode', () => {
    it('should display breadcrumb without "Confirmation" tab', async () => {
      // Given
      const stock = stockFactory()
      const offer = offerFactory({
        status: 'ACTIVE',
        subcategoryId: 'LIVRE_PAPIER',
      })
      jest.spyOn(api, 'getOffer').mockResolvedValue(offer)
      loadFakeApiStocks([stock])

      // When
      await renderOffer({ pathname: `/offre/${offer.id}/individuel/stocks` })

      // Then
      expect(await screen.getByTestId('bc-tab')).toBeInTheDocument()
      const detailTab = await screen.findByText("Détails de l'offre", {
        selector: 'a',
      })
      expect(detailTab).toBeInTheDocument()
      const stockTab = screen.getByText('Stocks et prix', { selector: 'a' })
      expect(stockTab).toBeInTheDocument()
      expect(stockTab.closest('.bc-step')).toHaveClass('active')
      expect(screen.queryByText('Confirmation')).not.toBeInTheDocument()
    })
  })
})

describe('confirmation step', () => {
  describe('in creation mode', () => {
    it('should not display breadcrumb', async () => {
      // Given
      const offer = offerFactory({
        name: 'mon offer',
        status: 'DRAFT',
        subcategoryId: 'LIVRE_PAPIER',
      })
      jest.spyOn(api, 'getOffer').mockResolvedValue(offer)

      // When
      await renderOffer({
        pathname: `/offre/${offer.id}/individuel/creation/confirmation`,
      })

      // Then
      expect(screen.queryByText("Détails de l'offre")).not.toBeInTheDocument()
    })
  })
})
