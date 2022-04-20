import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { configureTestStore } from 'store/testUtils'

import Header from '../Header'

const mockLogProClick = jest.fn()
const mockLogHomeClick = jest.fn()
const mockLogTicketClick = jest.fn()
const mockLogOfferClick = jest.fn()
const mockLogBookingClick = jest.fn()
const mockLogReimbursementClick = jest.fn()
const mockLogLogoutClick = jest.fn()

jest.mock('components/hooks/useAnalytics', () => {
  return jest.fn().mockReturnValue({
    logProClick: props => mockLogProClick(props),
    logHomeClick: props => mockLogHomeClick(props),
    logTicketClick: props => mockLogTicketClick(props),
    logOfferClick: props => mockLogOfferClick(props),
    logBookingClick: props => mockLogBookingClick(props),
    logReimbursementClick: props => mockLogReimbursementClick(props),
    logLogoutClick: props => mockLogLogoutClick(props),
  })
})

jest.mock('repository/pcapi/pcapi', () => ({
  signout: jest.fn().mockResolvedValue({}),
}))

const renderHeader = props => {
  const stubStore = configureTestStore()

  return render(
    <Provider store={stubStore}>
      <MemoryRouter initialEntries={['/accueil']}>
        <Header {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('navigation menu', () => {
  it('should have link to Styleguide when is enabled', () => {
    // When
    renderHeader({ isUserAdmin: false, isStyleguideActive: true })

    // Then
    expect(screen.queryByTestId('styleguide')).toBeInTheDocument()
  })

  it('should not have link to Styleguide when is disabled', () => {
    // When
    renderHeader({ isUserAdmin: false, isStyleguideActive: false })

    // Then
    expect(screen.queryByTestId('styleguide')).not.toBeInTheDocument()
  })

  describe('when clicking on Home icon', () => {
    it('should redirect to /accueil when user is not admin', () => {
      // When
      renderHeader({ isUserAdmin: false, isStyleguideActive: false })

      // Then
      expect(screen.getByText('Accueil').closest('a')).toHaveAttribute(
        'href',
        '/accueil'
      )
    })

    it('should redirect to /structures when user is admin', () => {
      // When
      renderHeader({ isUserAdmin: true, isStyleguideActive: false })

      // Then
      expect(screen.getByText('Accueil').closest('a')).toHaveAttribute(
        'href',
        '/structures'
      )
    })
  })

  describe('trackers should have been called 1 time with pathname', () => {
    it('when clicking on Pro', async () => {
      // given
      renderHeader({ isUserAdmin: false, isStyleguideActive: false })

      // When
      await userEvent.click(
        screen.getByAltText(
          "Pass Culture pro, l'espace Pass Culture des acteurs culturels"
        )
      )

      // Then
      expect(mockLogProClick).toHaveBeenCalledTimes(1)
      expect(mockLogProClick).toHaveBeenNthCalledWith(1, '/accueil')
    })

    it('when clicking on Home', async () => {
      // given
      renderHeader({ isUserAdmin: false, isStyleguideActive: false })

      // When
      await userEvent.click(screen.getByText('Accueil'))

      // Then
      expect(mockLogHomeClick).toHaveBeenCalledTimes(1)
      expect(mockLogHomeClick).toHaveBeenNthCalledWith(1, '/accueil')
    })

    it('when clicking on Ticket', async () => {
      // given
      renderHeader({ isUserAdmin: false, isStyleguideActive: false })

      // When
      await userEvent.click(screen.getByText('Guichet'))

      // Then
      expect(mockLogTicketClick).toHaveBeenCalledTimes(1)
      expect(mockLogTicketClick).toHaveBeenNthCalledWith(1, '/accueil')
    })

    it('when clicking on Offers', async () => {
      // given
      renderHeader({ isUserAdmin: false, isStyleguideActive: false })

      // When
      await userEvent.click(screen.getByText('Offres'))

      // Then
      expect(mockLogOfferClick).toHaveBeenCalledTimes(1)
      expect(mockLogOfferClick).toHaveBeenNthCalledWith(1, '/accueil')
    })

    it('when clicking on Bookings', async () => {
      // given
      renderHeader({ isUserAdmin: false, isStyleguideActive: false })

      // When
      await userEvent.click(screen.getByText('Réservations'))

      // Then
      expect(mockLogBookingClick).toHaveBeenCalledTimes(1)
      expect(mockLogBookingClick).toHaveBeenNthCalledWith(1, '/accueil')
    })

    it('when clicking on Reimbursement', async () => {
      // given
      renderHeader({ isUserAdmin: false, isStyleguideActive: false })

      // When
      await userEvent.click(screen.getByText('Remboursements'))

      // Then
      expect(mockLogReimbursementClick).toHaveBeenCalledTimes(1)
      expect(mockLogReimbursementClick).toHaveBeenNthCalledWith(1, '/accueil')
    })

    it('when clicking on Logout', async () => {
      // given
      renderHeader({ isUserAdmin: false, isStyleguideActive: false })

      // When
      await userEvent.click(screen.getAllByRole('menuitem')[5])

      // Then
      expect(mockLogLogoutClick).toHaveBeenCalledTimes(1)
      expect(mockLogLogoutClick).toHaveBeenNthCalledWith(1, '/accueil')
    })
  })
})
