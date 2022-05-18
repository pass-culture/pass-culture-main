import '@testing-library/jest-dom'

import * as useNotification from 'components/hooks/useNotification'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { updateAllOffersActiveStatus, updateOffersActiveStatus } from 'repository/pcapi/pcapi'

import ActionsBar from '../ActionsBar'
import {Provider} from 'react-redux'
import React from 'react'
import { configureTestStore } from 'store/testUtils'

const renderActionsBar = (props, store) => {
  return render(<Provider store={store}><ActionsBar {...props} /></Provider>)
}

jest.mock('repository/pcapi/pcapi', () => ({
  updateOffersActiveStatus: jest.fn().mockResolvedValue({}),
  updateAllOffersActiveStatus: jest.fn().mockResolvedValue({}),
}))



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
    store = configureTestStore({ offers: {searchFilters: {
      nameOrIsbn: 'keyword',
      venueId: 'E3',
      offererId: 'A4',
    }} })
  })

  it('should have buttons to activate and deactivate offers, and to abort action', () => {
    // when
    renderActionsBar(props, store)

    // then
    expect(
      screen.queryByText('Activer', { selector: 'button' })
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

  describe('on click on "Activer" button', () => {
    it('should activate selected offers', async () => {
      // given
      const notifySuccess = jest.fn()
      jest.spyOn(useNotification, 'default').mockImplementation(() => ({
        success: notifySuccess,
      }))
      renderActionsBar(props, store)

      // when
      fireEvent.click(screen.queryByText('Activer'))

      // then
      await waitFor(() => {
        expect(updateOffersActiveStatus).toHaveBeenLastCalledWith(
          ['testId1', 'testId2'],
          true
        )
        expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
        expect(props.refreshOffers).toHaveBeenCalled()
      })
      expect(notifySuccess).toHaveBeenCalledWith('2 offres ont bien été activées')
    })
  })

  describe('on click on "Désactiver" button', () => {
    it('should deactivate selected offers', async () => {
      // given
      const notifySuccess = jest.fn()
      jest.spyOn(useNotification, 'default').mockImplementation(() => ({
        success: notifySuccess,
      }))
      renderActionsBar(props, store)

      // when
      fireEvent.click(screen.queryByText('Désactiver'))

      // then
      await waitFor(() => {
        expect(updateOffersActiveStatus).toHaveBeenLastCalledWith(
          ['testId1', 'testId2'],
          false
        )
        expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
        expect(props.refreshOffers).toHaveBeenCalledWith()
      })
      expect(notifySuccess).toHaveBeenCalledWith('2 offres ont bien été désactivées')
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
    it('should activate all offers on click on "Activer" button', async () => {
      // given
      props.areAllOffersSelected = true
      renderActionsBar(props, store)
      const activateButton = screen.getByText('Activer')
      const expectedBody = {
        isActive: true,
        nameOrIsbn: 'keyword',
        offererId: 'A4',
        venueId: 'E3',
      }

      // when
      fireEvent.click(activateButton)

      // then
      await waitFor(() => {
        expect(updateAllOffersActiveStatus).toHaveBeenLastCalledWith(
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
      fireEvent.click(deactivateButton)

      // then
      await waitFor(() => {
        expect(updateAllOffersActiveStatus).toHaveBeenLastCalledWith(
          expectedBody
        )
        expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
        expect(props.refreshOffers).toHaveBeenCalledWith()
      })
    })
  })
})
