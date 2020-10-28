import '@testing-library/jest-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import { fetchFromApiWithCredentials } from 'utils/fetch'

import ActionsBar from '../ActionsBar'

const renderActionsBar = props => {
  return render(<ActionsBar {...props} />)
}

jest.mock('utils/fetch', () => ({
  fetchFromApiWithCredentials: jest.fn(),
}))

describe('src | components | pages | Offers | ActionsBar', () => {
  let props
  beforeEach(() => {
    props = {
      refreshOffers: jest.fn(),
      selectedOfferIds: ['testId1', 'testId2'],
      hideActionsBar: jest.fn(),
      setSelectedOfferIds: jest.fn(),
      toggleSelectAllCheckboxes: jest.fn(),
      showSuccessNotification: jest.fn(),
      trackActivateOffers: jest.fn(),
      trackDeactivateOffers: jest.fn(),
      searchFilters: {
        name: 'keyword',
        venueId: 'E3',
        offererId: 'A4',
        active: 'non',
      },
      switchAllOffersStatus: jest.fn(),
    }
  })

  it('should have buttons to activate and deactivate offers, and to abort action', () => {
    // when
    renderActionsBar(props)

    // then
    expect(screen.getByText('Activer')).toBeInTheDocument()
    expect(screen.getByText('Désactiver')).toBeInTheDocument()
    expect(screen.getByText('Annuler')).toBeInTheDocument()
  })

  it('should say of many offers are selected when only 1 offer is selected', () => {
    // given
    props.selectedOfferIds = ['testId']

    // when
    renderActionsBar(props)

    // then
    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say of many offers are selected when more than 1 offer are selected', () => {
    // when
    renderActionsBar(props)

    // then
    expect(screen.queryByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  describe('on click on "Activer" button', () => {
    it('should activate selected offers', async () => {
      // given
      renderActionsBar(props)
      const expectedBody = {
        ids: ['testId1', 'testId2'],
        isActive: true,
      }

      // when
      fireEvent.click(screen.queryByText('Activer'))

      // then
      await waitFor(() => {
        expect(fetchFromApiWithCredentials).toHaveBeenLastCalledWith(
          '/offers/active-status',
          'PATCH',
          expectedBody
        )
        expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
        expect(props.refreshOffers).toHaveBeenCalledWith({ shouldTriggerSpinner: false })
        expect(props.trackActivateOffers).toHaveBeenCalledWith(['testId1', 'testId2'])
      })
    })

    it('should hide action bar', async () => {
      // given
      renderActionsBar(props)

      // when
      fireEvent.click(screen.queryByText('Activer'))

      // then
      await waitFor(() => {
        expect(props.hideActionsBar).toHaveBeenCalledWith()
      })
    })

    it('should show notification with success message when only 1 offer is activated', async () => {
      // given
      props.selectedOfferIds = ['testId']
      renderActionsBar(props)

      // when
      fireEvent.click(screen.queryByText('Activer'))

      // then
      await waitFor(() => {
        expect(props.showSuccessNotification).toHaveBeenCalledWith('1 offre a bien été activée')
      })
    })

    it('should show notification with success message when more than 1 offer are activated', async () => {
      // given
      renderActionsBar(props)

      // when
      fireEvent.click(screen.queryByText('Activer'))

      // then
      await waitFor(() => {
        expect(props.showSuccessNotification).toHaveBeenCalledWith('2 offres ont bien été activées')
      })
    })
  })

  describe('on click on "Désactiver" button', () => {
    it('should deactivate selected offers', async () => {
      // given
      renderActionsBar(props)
      const expectedBody = {
        ids: ['testId1', 'testId2'],
        isActive: false,
      }

      // when
      fireEvent.click(screen.queryByText('Désactiver'))

      // then
      await waitFor(() => {
        expect(fetchFromApiWithCredentials).toHaveBeenLastCalledWith(
          '/offers/active-status',
          'PATCH',
          expectedBody
        )
        expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
        expect(props.refreshOffers).toHaveBeenCalledWith({ shouldTriggerSpinner: false })
        expect(props.trackDeactivateOffers).toHaveBeenCalledWith(['testId1', 'testId2'])
      })
    })

    it('should hide action bar', async () => {
      // given
      renderActionsBar(props)

      // when
      fireEvent.click(screen.queryByText('Désactiver'))

      // then
      await waitFor(() => {
        expect(props.hideActionsBar).toHaveBeenCalledWith()
      })
    })

    it('should show success notificiation with correct message when only 1 offer is deactivated', async () => {
      // given
      props.selectedOfferIds = ['testId']
      renderActionsBar(props)

      // when
      fireEvent.click(screen.queryByText('Désactiver'))

      // then
      await waitFor(() => {
        expect(props.showSuccessNotification).toHaveBeenCalledWith('1 offre a bien été désactivée')
      })
    })

    it('should show success notificiation with correct message when more than 1 offer are deactivated', async () => {
      // given
      renderActionsBar(props)

      // when
      fireEvent.click(screen.queryByText('Désactiver'))

      // then
      await waitFor(() => {
        expect(props.showSuccessNotification).toHaveBeenCalledWith(
          '2 offres ont bien été désactivées'
        )
      })
    })
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', () => {
    // given
    renderActionsBar(props)
    // when
    fireEvent.click(screen.queryByText('Annuler'))

    // then
    expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
    expect(props.hideActionsBar).toHaveBeenCalledWith()
  })

  describe('when all offers are selected', () => {
    it('should activate all offers on click on "Activer" button', async () => {
      // given
      props.areAllOffersSelected = true
      renderActionsBar(props)
      const activateButton = screen.queryByText('Activer')
      const expectedBody = {
        active: 'non',
        isActive: true,
        name: 'keyword',
        offererId: 'A4',
        venueId: 'E3',
      }

      // then
      expect(activateButton).not.toBeNull()

      // when
      fireEvent.click(activateButton)

      // then
      await waitFor(() => {
        expect(fetchFromApiWithCredentials).toHaveBeenLastCalledWith(
          '/offers/all-active-status',
          'PATCH',
          expectedBody
        )
        expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
        expect(props.hideActionsBar).toHaveBeenCalledWith()
        expect(props.refreshOffers).toHaveBeenCalledWith({ shouldTriggerSpinner: false })
      })
    })

    it('should deactivate all offers on click on "Désactiver" button', async () => {
      // given
      props.areAllOffersSelected = true
      renderActionsBar(props)
      const activateButton = screen.queryByText('Désactiver')
      const expectedBody = {
        active: 'non',
        isActive: false,
        name: 'keyword',
        offererId: 'A4',
        venueId: 'E3',
      }

      // then
      expect(activateButton).not.toBeNull()

      // when
      fireEvent.click(activateButton)

      // then
      await waitFor(() => {
        expect(fetchFromApiWithCredentials).toHaveBeenLastCalledWith(
          '/offers/all-active-status',
          'PATCH',
          expectedBody
        )
        expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
        expect(props.hideActionsBar).toHaveBeenCalledWith()
        expect(props.refreshOffers).toHaveBeenCalledWith({ shouldTriggerSpinner: false })
      })
    })
  })
})
