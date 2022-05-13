import '@testing-library/jest-dom'

import * as pcapi from 'repository/pcapi/pcapi'

import { render, screen } from '@testing-library/react'

import { Events } from 'core/FirebaseEvents/constants'
import Header from '../Header'
import { MemoryRouter } from 'react-router'
import { Provider } from 'react-redux'
import React from 'react'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

const mockLogEvent = jest.fn()
jest.mock('repository/pcapi/pcapi', () => ({
  signout: jest.fn(),
}))

const renderHeader = props => {
  const stubStore = configureTestStore({ app: { logEvent: mockLogEvent } })

  return render(
    <Provider store={stubStore}>
      <MemoryRouter initialEntries={['/accueil']}>
        <Header {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('navigation menu', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('when clicking on Home icon', () => {
    it('should redirect to /accueil when user is not admin', () => {
      // When
      renderHeader({ isUserAdmin: false })

      // Then
      expect(screen.getByText('Accueil').closest('a')).toHaveAttribute(
        'href',
        '/accueil'
      )
    })

    it('should redirect to /structures when user is admin', () => {
      // When
      renderHeader({ isUserAdmin: true })

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
      renderHeader({ isUserAdmin: false })

      // When
      await userEvent.click(
        screen.getByAltText(
          "Pass Culture pro, l'espace Pass Culture des acteurs culturels"
        )
      )

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_PRO, {
        from: '/accueil',
      })
    })

    it('when clicking on Home', async () => {
      // given
      renderHeader({ isUserAdmin: false })

      // When
      await userEvent.click(screen.getByText('Accueil'))

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_HOME, {
        from: '/accueil',
      })
    })

    it('when clicking on Ticket', async () => {
      // given
      renderHeader({ isUserAdmin: false })

      // When
      await userEvent.click(screen.getByText('Guichet'))

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_TICKET, {
        from: '/accueil',
      })
    })

    it('when clicking on Offers', async () => {
      // given
      renderHeader({ isUserAdmin: false })

      // When
      await userEvent.click(screen.getByText('Offres'))

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_OFFER, {
        from: '/accueil',
      })
    })

    it('when clicking on Bookings', async () => {
      // given
      renderHeader({ isUserAdmin: false })

      // When
      await userEvent.click(screen.getByText('Réservations'))

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_BOOKING, {
        from: '/accueil',
      })
    })

    it('when clicking on Reimbursement', async () => {
      // given
      renderHeader({ isUserAdmin: false })

      // When
      await userEvent.click(screen.getByText('Remboursements'))

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_REIMBURSEMENT,
        { from: '/accueil' }
      )
    })

    it('when clicking on Logout', async () => {
      // given
      renderHeader({ isUserAdmin: false })
      pcapi.signout.mockResolvedValue({})

      // When
      await userEvent.click(screen.getAllByRole('menuitem')[5])

      // Then
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(1, Events.CLICKED_LOGOUT, {
        from: '/accueil',
      })
    })
  })
})
