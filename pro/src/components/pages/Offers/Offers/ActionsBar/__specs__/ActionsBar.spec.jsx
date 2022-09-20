import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { api } from 'apiClient/api'
import * as useAnalytics from 'components/hooks/useAnalytics'
import * as useNotification from 'components/hooks/useNotification'
import { Events } from 'core/FirebaseEvents/constants'
import { configureTestStore } from 'store/testUtils'

import ActionsBar from '../ActionsBar'

const renderActionsBar = (props, store) => {
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/offres']}>
        <ActionsBar {...props} />
      </MemoryRouter>
    </Provider>
  )
}

jest.mock('apiClient/api', () => ({
  api: {
    patchOffersActiveStatus: jest.fn().mockResolvedValue({}),
    patchAllOffersActiveStatus: jest.fn().mockResolvedValue({}),
  },
}))

const mockLogEvent = jest.fn()

describe('src | components | pages | Offers | ActionsBar', () => {
  let props
  let store
  beforeEach(() => {
    props = {
      refreshOffers: jest.fn(),
      selectedOfferIds: ['testId1', 'testId2'],
      clearSelectedOfferIds: jest.fn(),
      toggleSelectAllCheckboxes: jest.fn(),
      showSuccessNotification: jest.fn(),
      showPendingNotification: jest.fn(),
      switchAllOffersStatus: jest.fn(),
      nbSelectedOffers: 2,
    }
    store = configureTestStore({
      offers: {
        searchFilters: {
          nameOrIsbn: 'keyword',
          venueId: 'E3',
          offererId: 'A4',
        },
      },
    })
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should have buttons to activate and deactivate offers, and to abort action', () => {
    // when
    renderActionsBar(props, store)

    // then
    expect(
      screen.queryByText('Publier', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Désactiver', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Annuler', { selector: 'button' })
    ).toBeInTheDocument()
  })

  it('should say how many offers are selected when only 1 offer is selected', () => {
    // given
    props.nbSelectedOffers = 1

    // when
    renderActionsBar(props, store)

    // then
    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
    // when
    renderActionsBar(props, store)

    // then
    expect(screen.queryByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 500 offers are selected', () => {
    // given
    props.nbSelectedOffers = 501

    // when
    renderActionsBar(props, store)

    // then
    expect(screen.queryByText('500+ offres sélectionnées')).toBeInTheDocument()
  })

  describe('on click on "Publier" button', () => {
    it('should activate selected offers', async () => {
      // given
      const notifySuccess = jest.fn()
      jest.spyOn(useNotification, 'default').mockImplementation(() => ({
        success: notifySuccess,
      }))
      renderActionsBar(props, store)

      // when
      await userEvent.click(screen.queryByText('Publier'))

      // then
      await waitFor(() => {
        expect(api.patchOffersActiveStatus).toHaveBeenLastCalledWith({
          ids: ['testId1', 'testId2'],
          isActive: true,
        })
        expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
        expect(props.refreshOffers).toHaveBeenCalled()
      })
      expect(notifySuccess).toHaveBeenCalledWith(
        '2 offres ont bien été publiées'
      )
    })
  })

  describe('on click on "Désactiver" button', () => {
    it('should deactivate selected offers', async () => {
      // given
      props.areAllOffersSelected = false
      const notifySuccess = jest.fn()
      jest.spyOn(useNotification, 'default').mockImplementation(() => ({
        success: notifySuccess,
      }))
      renderActionsBar(props, store)

      // when
      await userEvent.click(screen.queryByText('Désactiver'))
      const confirmDeactivateButton = screen.getAllByText('Désactiver')[1]
      await userEvent.click(confirmDeactivateButton)

      // then
      await waitFor(() => {
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_DISABLED_SELECTED_OFFERS,
          {
            from: '/offres',
            has_selected_all_offers: false,
          }
        )
        expect(api.patchOffersActiveStatus).toHaveBeenLastCalledWith({
          ids: ['testId1', 'testId2'],
          isActive: false,
        })
        expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
        expect(props.refreshOffers).toHaveBeenCalledWith()
      })
      expect(notifySuccess).toHaveBeenCalledWith(
        '2 offres ont bien été désactivées'
      )
    })
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', () => {
    // given
    renderActionsBar(props, store)
    // when
    fireEvent.click(screen.queryByText('Annuler'))

    // then
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
  })

  describe('when all offers are selected', () => {
    it('should activate all offers on click on "Publier" button', async () => {
      // given
      props.areAllOffersSelected = true

      renderActionsBar(props, store)
      const activateButton = screen.getByText('Publier')
      const expectedBody = {
        isActive: true,
        nameOrIsbn: 'keyword',
        offererId: 'A4',
        venueId: 'E3',
      }

      // when
      await userEvent.click(activateButton)

      // then
      await waitFor(() => {
        expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
          expectedBody
        )
        expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
        expect(props.refreshOffers).toHaveBeenCalledWith()
      })
    })
    it('should deactivate all offers on click on "Désactiver" button', async () => {
      // given
      props.areAllOffersSelected = true
      renderActionsBar(props, store)
      const deactivateButton = screen.getByText('Désactiver')
      const expectedBody = {
        isActive: false,
        nameOrIsbn: 'keyword',
        offererId: 'A4',
        venueId: 'E3',
      }

      // when
      await userEvent.click(deactivateButton)
      const confirmDeactivateButton = screen.getAllByText('Désactiver')[1]
      await userEvent.click(confirmDeactivateButton)

      // then
      await waitFor(() => {
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_DISABLED_SELECTED_OFFERS,
          {
            from: '/offres',
            has_selected_all_offers: true,
          }
        )
        expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
          expectedBody
        )
        expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
        expect(props.refreshOffers).toHaveBeenCalledWith()
      })
    })
    it('should track cancel all offers on click on "Annuler" button', async () => {
      // given
      props.areAllOffersSelected = true
      renderActionsBar(props, store)
      const deactivateButton = screen.getByText('Désactiver')

      // when
      await userEvent.click(deactivateButton)
      const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
      await userEvent.click(cancelDeactivateButton)

      // then
      await waitFor(() => {
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_CANCELED_SELECTED_OFFERS,
          {
            from: '/offres',
            has_selected_all_offers: true,
          }
        )
      })
    })
    it('should track cancel offer on click on "Annuler" button', async () => {
      // given
      props.areAllOffersSelected = false
      renderActionsBar(props, store)
      const deactivateButton = screen.getByText('Désactiver')

      // when
      await userEvent.click(deactivateButton)
      const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
      await userEvent.click(cancelDeactivateButton)

      // then
      await waitFor(() => {
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          Events.CLICKED_CANCELED_SELECTED_OFFERS,
          {
            from: '/offres',
            has_selected_all_offers: false,
          }
        )
      })
    })
  })
})
