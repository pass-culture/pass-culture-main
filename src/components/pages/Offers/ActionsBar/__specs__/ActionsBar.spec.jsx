import '@testing-library/jest-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import { updateOffersActiveStatus } from 'repository/pcapi/pcapi'

import ActionsBar from '../ActionsBar'

const renderActionsBar = props => {
  return render(<ActionsBar {...props} />)
}

jest.mock('repository/pcapi/pcapi', () => ({
  updateOffersActiveStatus: jest.fn().mockResolvedValue({}),
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
      nbSelectedOffers: 2,
    }
  })

  it('should have buttons to activate and deactivate offers, and to abort action', () => {
    // when
    renderActionsBar(props)

    // then
    expect(screen.queryByText('Activer', { selector: 'button' })).toBeInTheDocument()
    expect(screen.queryByText('Désactiver', { selector: 'button' })).toBeInTheDocument()
    expect(screen.queryByText('Annuler', { selector: 'button' })).toBeInTheDocument()
  })

  it('should say how many offers are selected when only 1 offer is selected', () => {
    // given
    props.nbSelectedOffers = 1

    // when
    renderActionsBar(props)

    // then
    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
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
        expect(updateOffersActiveStatus).toHaveBeenLastCalledWith(false, expectedBody)
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
      props.nbSelectedOffers = 1
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
        expect(updateOffersActiveStatus).toHaveBeenLastCalledWith(false, expectedBody)
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
      props.nbSelectedOffers = 1
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
      const activateButton = screen.getByText('Activer')
      const expectedBody = {
        active: 'non',
        isActive: true,
        name: 'keyword',
        offererId: 'A4',
        venueId: 'E3',
      }

      // when
      fireEvent.click(activateButton)

      // then
      await waitFor(() => {
        expect(updateOffersActiveStatus).toHaveBeenLastCalledWith(true, expectedBody)
        expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
        expect(props.hideActionsBar).toHaveBeenCalledTimes(1)
        expect(props.refreshOffers).toHaveBeenCalledWith({ shouldTriggerSpinner: false })
      })
    })

    it('should deactivate all offers on click on "Désactiver" button', async () => {
      // given
      props.areAllOffersSelected = true
      renderActionsBar(props)
      const deactivateButton = screen.getByText('Désactiver')
      const expectedBody = {
        active: 'non',
        isActive: false,
        name: 'keyword',
        offererId: 'A4',
        venueId: 'E3',
      }

      // when
      fireEvent.click(deactivateButton)

      // then
      await waitFor(() => {
        expect(updateOffersActiveStatus).toHaveBeenLastCalledWith(true, expectedBody)
        expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
        expect(props.hideActionsBar).toHaveBeenCalledTimes(1)
        expect(props.refreshOffers).toHaveBeenCalledWith({ shouldTriggerSpinner: false })
      })
    })
  })
})
