import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'

import * as useNotification from 'components/hooks/useNotification'
import {
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_INACTIVE,
} from 'core/Offers/constants'
import * as pcapi from 'repository/pcapi/pcapi'
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
      <MemoryRouter>
        <StatusToggleButton offer={offer} reloadOffer={jest.fn()} />
      </MemoryRouter>
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
      .spyOn(pcapi, 'updateOffersActiveStatus')
      .mockResolvedValue()
    const notifySuccess = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: notifySuccess,
    }))

    // when
    renderStatusToggleButton(offer)

    // then
    fireEvent.click(screen.getByRole('button', { name: /Désactiver/ }))

    expect(toggle).toHaveBeenCalledTimes(1)
    expect(toggle).toHaveBeenNthCalledWith(1, ['AG3A'], false)
    await waitFor(() =>
      expect(notifySuccess).toHaveBeenNthCalledWith(
        1,
        'L’offre a bien été désactivée.'
      )
    )
  })
  it('should activate an offer and confirm', async () => {
    // given
    const toggleFunction = jest
      .spyOn(pcapi, 'updateOffersActiveStatus')
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
    fireEvent.click(screen.getByText(/Publier/))
    expect(toggleFunction).toHaveBeenCalledTimes(1)
    expect(toggleFunction).toHaveBeenNthCalledWith(1, ['AG3A'], true)
    await waitFor(() =>
      expect(notifySuccess).toHaveBeenNthCalledWith(
        1,
        'L’offre a bien été publiée.'
      )
    )
  })
  it('should display error', async () => {
    // given
    const toggleFunction = jest
      .spyOn(pcapi, 'updateOffersActiveStatus')
      .mockRejectedValue()
    const notifyError = jest.fn()
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))
    // when
    renderStatusToggleButton(offer)

    // then
    fireEvent.click(screen.getByText(/Désactiver/))
    expect(toggleFunction).toHaveBeenCalledTimes(1)
    await waitFor(() =>
      expect(notifyError).toHaveBeenNthCalledWith(
        1,
        'Une erreur est survenue, veuillez réessayer ultérieurement.'
      )
    )
  })
})
