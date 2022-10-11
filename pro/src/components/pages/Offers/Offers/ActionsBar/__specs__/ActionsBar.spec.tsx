import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'
import type { Store } from 'redux'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNotification from 'hooks/useNotification'
import { configureTestStore } from 'store/testUtils'

import ActionsBar, { IActionBarProps } from '../ActionsBar'

interface IRenderActionsBar {
  props: IActionBarProps
  store: Store
}

const renderActionsBar = ({ props, store }: IRenderActionsBar) =>
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/offres']}>
        <ActionsBar {...props} />
      </MemoryRouter>
    </Provider>
  )

jest.mock('apiClient/api', () => ({
  api: {
    patchOffersActiveStatus: jest.fn().mockResolvedValue({}),
    patchAllOffersActiveStatus: jest.fn().mockResolvedValue({}),
  },
}))

const mockLogEvent = jest.fn()
const mockCanUpdatedOfferStatus = jest.fn().mockReturnValue(true)
const mockCanDeleteOffers = jest.fn().mockReturnValue(true)

describe('src | components | pages | Offers | ActionsBar', () => {
  let props: IActionBarProps
  let store: Store
  const mockUseNotification = {
    close: jest.fn(),
    error: jest.fn(),
    pending: jest.fn(),
    information: jest.fn(),
    success: jest.fn(),
  }

  beforeEach(() => {
    props = {
      canUpdateOffersStatus: mockCanUpdatedOfferStatus,
      refreshOffers: jest.fn(),
      selectedOfferIds: ['testId1', 'testId2'],
      clearSelectedOfferIds: jest.fn(),
      toggleSelectAllCheckboxes: jest.fn(),
      nbSelectedOffers: 2,
      areAllOffersSelected: false,
      audience: Audience.INDIVIDUAL,
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
    renderActionsBar({ props, store })

    screen.getByText('Publier', { selector: 'button' })

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
    renderActionsBar({ props, store })

    // then
    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
    // when
    renderActionsBar({ props, store })

    // then
    expect(screen.queryByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 500 offers are selected', () => {
    // given
    props.nbSelectedOffers = 501

    // when
    renderActionsBar({ props, store })

    // then
    expect(screen.queryByText('500+ offres sélectionnées')).toBeInTheDocument()
  })

  describe('on click on "Publier" button', () => {
    it('should activate selected offers', async () => {
      // given
      const notifySuccess = jest.fn()
      jest.spyOn(useNotification, 'default').mockImplementation(() => ({
        ...mockUseNotification,
        success: notifySuccess,
      }))
      renderActionsBar({ props, store })

      // when
      await userEvent.click(screen.getByText('Publier'))

      // then
      expect(api.patchOffersActiveStatus).toHaveBeenLastCalledWith({
        ids: ['testId1', 'testId2'],
        isActive: true,
      })
      expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
      expect(props.refreshOffers).toHaveBeenCalled()
      expect(notifySuccess).toHaveBeenCalledWith(
        '2 offres ont bien été publiées'
      )
    })
    it('should not activate offers when a draft is selected', async () => {
      // given
      const notifyError = jest.fn()
      jest.spyOn(useNotification, 'default').mockImplementation(() => ({
        ...mockUseNotification,
        error: notifyError,
      }))
      mockCanUpdatedOfferStatus.mockReturnValueOnce(false)

      renderActionsBar({ props, store })

      // when
      await userEvent.click(screen.getByText('Publier'))

      // then
      expect(api.patchOffersActiveStatus).not.toHaveBeenCalled()
      expect(props.clearSelectedOfferIds).not.toHaveBeenCalled()
      expect(props.refreshOffers).not.toHaveBeenCalled()
      expect(notifyError).toHaveBeenCalledWith(
        'Vous ne pouvez pas publier des brouillons depuis cette liste'
      )
    })
  })

  describe('on click on "Désactiver" button', () => {
    it('should deactivate selected offers', async () => {
      // given
      props.areAllOffersSelected = false
      const notifySuccess = jest.fn()
      jest.spyOn(useNotification, 'default').mockImplementation(() => ({
        ...mockUseNotification,
        success: notifySuccess,
      }))
      renderActionsBar({ props, store })

      // when
      await userEvent.click(screen.getByText('Désactiver'))
      const confirmDeactivateButton = screen.getAllByText('Désactiver')[1]
      await userEvent.click(confirmDeactivateButton)

      // then
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

      expect(notifySuccess).toHaveBeenCalledWith(
        '2 offres ont bien été désactivées'
      )
    })
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', async () => {
    // given
    renderActionsBar({ props, store })

    // when
    await userEvent.click(screen.getByText('Annuler'))

    // then
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
  })

  describe('when all offers are selected', () => {
    it('should activate all offers on click on "Publier" button', async () => {
      // given
      props.areAllOffersSelected = true

      renderActionsBar({ props, store })
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
      expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
        expectedBody
      )
      expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
      expect(props.refreshOffers).toHaveBeenCalledWith()
    })
    it('should deactivate all offers on click on "Désactiver" button', async () => {
      // given
      props.areAllOffersSelected = true
      renderActionsBar({ props, store })
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

    it('should track cancel all offers on click on "Annuler" button', async () => {
      // given
      props.areAllOffersSelected = true
      renderActionsBar({ props, store })
      const deactivateButton = screen.getByText('Désactiver')

      // when
      await userEvent.click(deactivateButton)
      const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
      await userEvent.click(cancelDeactivateButton)

      // then
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

    it('should track cancel offer on click on "Annuler" button', async () => {
      // given
      props.areAllOffersSelected = false
      renderActionsBar({ props, store })
      const deactivateButton = screen.getByText('Désactiver')

      // when
      await userEvent.click(deactivateButton)
      const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
      await userEvent.click(cancelDeactivateButton)

      // then
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
