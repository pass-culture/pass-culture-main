import '@testing-library/jest-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'

import * as fetchUtils from 'utils/fetch'

import ActionsBar from '../ActionsBar'

const renderActionsBar = props => {
  return render(<ActionsBar {...props} />)
}

jest.spyOn(fetchUtils, 'fetchFromApiWithCredentials').mockImplementation(() => Promise.resolve())

describe('src | components | pages | Offers | ActionsBar', () => {
  let props
  beforeEach(() => {
    props = {
      refreshOffers: jest.fn(),
      selectedOfferIds: ['testId1', 'testId2'],
      hideActionsBar: jest.fn(),
      setSelectedOfferIds: jest.fn(),
      trackActivateOffers: jest.fn(),
      trackDeactivateOffers: jest.fn(),
    }
  })

  it('should activate selected offers on click on "Activer" button', async () => {
    // given
    renderActionsBar(props)
    const activateButton = screen.queryByText('Activer')
    const expectedBody = {
      ids: ['testId1', 'testId2'],
      isActive: true,
    }

    // then
    expect(activateButton).not.toBeNull()

    // when
    fireEvent.click(activateButton)

    // then
    await waitFor(() => {
      expect(fetchUtils.fetchFromApiWithCredentials).toHaveBeenLastCalledWith(
        '/offers/active-status',
        'PATCH',
        expectedBody
      )
      expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
      expect(props.hideActionsBar).toHaveBeenCalledWith()
      expect(props.refreshOffers).toHaveBeenCalledWith({ shouldTriggerSpinner: false })
      expect(props.trackActivateOffers).toHaveBeenCalledWith(['testId1', 'testId2'])
    })
  })

  it('should deactivate selected offers on click on "Désactiver" button', async () => {
    // given
    renderActionsBar(props)
    const activateButton = screen.queryByText('Désactiver')
    const expectedBody = {
      ids: ['testId1', 'testId2'],
      isActive: false,
    }

    // then
    expect(activateButton).not.toBeNull()

    // when
    fireEvent.click(activateButton)

    // then
    await waitFor(() => {
      expect(fetchUtils.fetchFromApiWithCredentials).toHaveBeenLastCalledWith(
        '/offers/active-status',
        'PATCH',
        expectedBody
      )
      expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
      expect(props.hideActionsBar).toHaveBeenCalledWith()
      expect(props.refreshOffers).toHaveBeenCalledWith({ shouldTriggerSpinner: false })
      expect(props.trackDeactivateOffers).toHaveBeenCalledWith(['testId1', 'testId2'])
    })
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', () => {
    // given
    renderActionsBar(props)
    const cancelButton = screen.queryByText('Annuler')

    // then
    expect(cancelButton).not.toBeNull()

    // when
    fireEvent.click(cancelButton)

    // then
    expect(props.setSelectedOfferIds).toHaveBeenNthCalledWith(1, [])
    expect(props.hideActionsBar).toHaveBeenCalledWith()
  })
})
