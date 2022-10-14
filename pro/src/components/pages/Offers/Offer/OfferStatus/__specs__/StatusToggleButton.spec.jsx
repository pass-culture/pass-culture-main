import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import { api } from 'apiClient/api'
import {
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_INACTIVE,
} from 'core/Offers/constants'
import * as useNotification from 'hooks/useNotification'
import { configureTestStore } from 'store/testUtils'

import StatusToggleButton from '../StatusToggleButton'

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offerId: 'BQ',
  }),
}))

const renderStatusToggleButton = (offer, store) => {
  render(
    <Provider store={configureTestStore(store)}>
      <StatusToggleButton offer={offer} reloadOffer={jest.fn()} />
    </Provider>
  )
}
describe('StatusToggleButton', () => {
  let offer
  beforeEach(() => {
    offer = {
      id: 'AG3A',
      isActive: true,
      status: OFFER_STATUS_ACTIVE,
    }
  })

  it('should deactivate an offer and confirm', async () => {
    // given
    const toggle = jest
      .spyOn(api, 'patchOffersActiveStatus')
      .mockResolvedValue()
    const notifySuccess = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: notifySuccess,
    }))

    // when
    renderStatusToggleButton(offer)

    // then
    await userEvent.click(screen.getByRole('button', { name: /Désactiver/ }))

    expect(toggle).toHaveBeenCalledTimes(1)
    expect(toggle).toHaveBeenNthCalledWith(1, {
      ids: ['AG3A'],
      isActive: false,
    })

    expect(notifySuccess).toHaveBeenNthCalledWith(
      1,
      'L’offre a bien été désactivée.'
    )
  })
  it('should activate an offer and confirm', async () => {
    // given
    const toggleFunction = jest
      .spyOn(api, 'patchOffersActiveStatus')
      .mockResolvedValue()
    const notifySuccess = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: notifySuccess,
    }))
    // when
    renderStatusToggleButton({
      ...offer,
      isActive: false,
      status: OFFER_STATUS_INACTIVE,
    })

    // then
    await userEvent.click(screen.getByText(/Publier/))
    expect(toggleFunction).toHaveBeenCalledTimes(1)
    expect(toggleFunction).toHaveBeenNthCalledWith(1, {
      ids: ['AG3A'],
      isActive: true,
    })
    expect(notifySuccess).toHaveBeenNthCalledWith(
      1,
      'L’offre a bien été publiée.'
    )
  })
  it('should display error', async () => {
    // given
    const toggleFunction = jest
      .spyOn(api, 'patchOffersActiveStatus')
      .mockRejectedValue()
    const notifyError = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))
    // when
    renderStatusToggleButton(offer)

    // then
    await userEvent.click(screen.getByText(/Désactiver/))
    expect(toggleFunction).toHaveBeenCalledTimes(1)
    expect(notifyError).toHaveBeenNthCalledWith(
      1,
      'Une erreur est survenue, veuillez réessayer ultérieurement.'
    )
  })
})
