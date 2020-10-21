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
      showSuccessNotification: jest.fn(),
      trackActivateOffers: jest.fn(),
      trackDeactivateOffers: jest.fn(),
    }
  })

  it('should have buttons to activate and deactivate offers, and to abort action', () => {
    // when
    renderActionsBar(props)

    // then
    expect(screen.queryByText('Activer')).toBeInTheDocument()
    expect(screen.queryByText('Désactiver')).toBeInTheDocument()
    expect(screen.queryByText('Annuler')).toBeInTheDocument()
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

    it('should show success notificiation with correct message', async () => {
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

    it('should show success notificiation with correct message', async () => {
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
})
