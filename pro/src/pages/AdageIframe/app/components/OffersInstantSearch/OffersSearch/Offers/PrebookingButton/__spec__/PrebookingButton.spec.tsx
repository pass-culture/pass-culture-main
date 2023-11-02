import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { OfferStockResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import Notification from 'components/Notification/Notification'
import { renderWithProviders } from 'utils/renderWithProviders'

import PrebookingButton from '../PrebookingButton'

vi.mock('repository/pcapi/pcapi', () => ({
  preBookStock: vi.fn(),
}))
vi.mock('pages/AdageIframe/libs/initAlgoliaAnalytics')

vi.mock('apiClient/api', () => ({
  apiAdage: {
    bookCollectiveOffer: vi.fn(),
    logBookingModalButtonClick: vi.fn(),
  },
}))

vi.mock('utils/config', async () => {
  return {
    ...((await vi.importActual('utils/config')) ?? {}),
    LOGS_DATA: true,
  }
})

describe('offer', () => {
  let stock: OfferStockResponse
  beforeEach(() => {
    stock = {
      id: 117,
      beginningDatetime: '03/01/2023',
      bookingLimitDatetime: '01/01/2023',
      isBookable: true,
      price: 20,
      numberOfTickets: 3,
      educationalPriceDetail: '1200',
    }
  })

  describe('offer item', () => {
    it('should not display when prebooking is not activated', () => {
      // Given
      renderWithProviders(
        <PrebookingButton
          canPrebookOffers={false}
          offerId={1}
          queryId="aez"
          stock={stock}
        />
      )
      // When - Then
      expect(screen.queryByText('Préréserver')).not.toBeInTheDocument()
    })

    it('should display when prebooking is activated', () => {
      // Given
      renderWithProviders(
        <PrebookingButton
          canPrebookOffers
          offerId={1}
          queryId="aez"
          stock={stock}
        />
      )
      // When - Then
      expect(screen.getByText('Préréserver')).toBeInTheDocument()
    })
    it('should display modal on click', async () => {
      // Given
      renderWithProviders(
        <PrebookingButton
          canPrebookOffers
          offerId={1}
          queryId="aez"
          stock={stock}
        />
      )
      // When
      const preBookButton = screen.getByRole('button', { name: 'Préréserver' })
      await userEvent.click(preBookButton)

      // Then
      expect(
        screen.getByText('Êtes-vous sûr de vouloir préréserver ?')
      ).toBeInTheDocument()
    })

    it('should display error message if uai does not match', async () => {
      // Given
      renderWithProviders(
        <>
          <PrebookingButton
            canPrebookOffers
            offerId={1}
            queryId="aez"
            stock={stock}
          />
          <Notification />
        </>
      )
      // When
      const preBookButton = screen.getByRole('button', { name: 'Préréserver' })
      await userEvent.click(preBookButton)

      // Then
      expect(
        screen.getByText('Êtes-vous sûr de vouloir préréserver ?')
      ).toBeInTheDocument()

      vi.spyOn(apiAdage, 'bookCollectiveOffer').mockRejectedValueOnce({
        statusCode: 400,
        body: { code: 'WRONG_UAI_CODE' },
      })
      await userEvent.click(screen.getByRole('button', { name: 'Préréserver' }))

      expect(
        screen.getByText(
          'Cette offre n’est pas préréservable par votre établissement'
        )
      ).toBeInTheDocument()
    })

    it('should display a success message notification when booking worked', async () => {
      vi.spyOn(apiAdage, 'bookCollectiveOffer').mockResolvedValue({
        bookingId: 123,
      })
      // Given
      renderWithProviders(
        <>
          <PrebookingButton
            canPrebookOffers
            offerId={1}
            queryId="aez"
            stock={stock}
          />
          <Notification />
        </>
      )
      // When
      const preBookButton = screen.getByRole('button', { name: 'Préréserver' })
      await userEvent.click(preBookButton)

      // Then
      expect(
        screen.getByText('Êtes-vous sûr de vouloir préréserver ?')
      ).toBeInTheDocument()

      await userEvent.click(screen.getByRole('button', { name: 'Préréserver' }))

      expect(
        screen.getByText('Votre préréservation a été effectuée avec succès')
      ).toBeInTheDocument()
    })

    it('should log info when clicking "préréserver" button ', async () => {
      renderWithProviders(
        <>
          <PrebookingButton
            canPrebookOffers
            offerId={1}
            queryId="aez"
            stock={stock}
            isInSuggestions={false}
          />
          <Notification />
        </>
      )

      const preBookButton = screen.getByRole('button', { name: 'Préréserver' })
      await userEvent.click(preBookButton)

      expect(apiAdage.logBookingModalButtonClick).toHaveBeenCalledWith({
        iframeFrom: '/',
        isFromNoResult: false,
        queryId: 'aez',
        stockId: 117,
      })
    })

    it('should log info when clicking "préréserver" button for no result page suggestion', async () => {
      renderWithProviders(
        <>
          <PrebookingButton
            canPrebookOffers
            offerId={1}
            queryId="aez"
            stock={stock}
            isInSuggestions={true}
          />
          <Notification />
        </>
      )

      const preBookButton = screen.getByRole('button', { name: 'Préréserver' })
      await userEvent.click(preBookButton)

      expect(apiAdage.logBookingModalButtonClick).toHaveBeenCalledWith({
        iframeFrom: '/',
        isFromNoResult: true,
        queryId: 'aez',
        stockId: 117,
      })
    })
  })
})
