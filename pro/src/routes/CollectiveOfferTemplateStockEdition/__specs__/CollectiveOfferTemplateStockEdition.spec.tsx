import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { History } from 'history'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  TOTAL_PRICE_LABEL,
} from 'screens/OfferEducationalStock/constants/labels'
import { configureTestStore } from 'store/testUtils'

import CollectiveOfferTemplateStockEdition from '../CollectiveOfferTemplateStockEdition'

const mockHistoryPush = jest.fn()

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offerId: 'T-A1',
  }),
  useHistory: () => ({
    push: mockHistoryPush,
  }),
}))

jest.mock('apiClient/api', () => ({
  api: {
    transformCollectiveOfferTemplateIntoCollectiveOffer: jest
      .fn()
      .mockResolvedValue({ offerId: 'B1' }),
    getCollectiveOfferTemplate: jest.fn().mockResolvedValue({
      id: 'T-A1',
      venue: {
        managinOfferer: { id: 'A1' },
      },
    }),
  },
}))

describe('CollectiveOfferTemplateStockEdition', () => {
  let history: History

  beforeAll(() => {
    history = createBrowserHistory()
  })
  it('should redirect to visibility edition page after turning template offer into collective offer', async () => {
    render(
      <Router history={history}>
        <Provider store={configureTestStore({})}>
          <CollectiveOfferTemplateStockEdition />
        </Provider>
      </Router>
    )

    await waitFor(() =>
      expect(
        screen.getByLabelText('Je connais la date et le prix de mon offre')
      ).toBeInTheDocument()
    )

    const classicOfferButton = (await screen.findByLabelText(
      'Je connais la date et le prix de mon offre'
    )) as HTMLInputElement

    await userEvent.click(classicOfferButton)
    await waitFor(() => expect(classicOfferButton.checked).toBe(true))

    const beginningDate = screen.getByLabelText(EVENT_DATE_LABEL)
    const beginningTime = screen.getByLabelText(EVENT_TIME_LABEL)
    const numberOfPlaces = screen.getByLabelText(NUMBER_OF_PLACES_LABEL)
    const price = screen.getByLabelText(TOTAL_PRICE_LABEL)

    await userEvent.click(beginningDate)
    const options = screen.getAllByRole('option')
    const enabledOptions = options.filter(option => {
      return option.getAttribute('aria-disabled') === 'false'
    })
    await userEvent.click(enabledOptions[0])

    await userEvent.type(beginningTime, '10:00')
    await userEvent.type(numberOfPlaces, '30')
    await userEvent.type(price, '30')

    const submitButton = screen.getByRole('button', { name: 'Enregistrer' })
    expect(submitButton).toBeEnabled()

    await userEvent.click(submitButton)
    expect(
      api.transformCollectiveOfferTemplateIntoCollectiveOffer
    ).toHaveBeenCalled()
    await waitFor(() => {
      expect(mockHistoryPush).toHaveBeenCalledWith(
        '/offre/B1/collectif/visibilite/edition'
      )
    })
  })
})
