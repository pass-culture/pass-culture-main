import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { History } from 'history'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Router } from 'react-router-dom'

import { api } from 'apiClient/api'
import { CollectiveOfferTemplate } from 'core/OfferEducational'
import { configureTestStore } from 'store/testUtils'
import { collectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'

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
    editCollectiveOfferTemplate: jest.fn().mockResolvedValue({ offerId: 'B1' }),
  },
}))

describe('CollectiveOfferTemplateStockEdition', () => {
  let history: History
  const offer: CollectiveOfferTemplate = collectiveOfferTemplateFactory({
    educationalPriceDetail: 'le détail de mon prix',
  })

  beforeAll(() => {
    history = createBrowserHistory()
  })
  it('should prefill form and call patchCollectiveOffer', async () => {
    render(
      <Router history={history}>
        <Provider store={configureTestStore({})}>
          <CollectiveOfferTemplateStockEdition
            offer={offer}
            reloadCollectiveOffer={jest.fn()}
          />
        </Provider>
      </Router>
    )

    const priceDetailsInput = screen.getByLabelText(/Détails/)
    expect(priceDetailsInput).toHaveValue('le détail de mon prix')
    await userEvent.clear(priceDetailsInput)
    await userEvent.type(priceDetailsInput, 'bla bla bla')

    const submitButton = screen.getByRole('button', { name: 'Enregistrer' })
    expect(submitButton).toBeEnabled()

    await userEvent.click(submitButton)
    expect(api.editCollectiveOfferTemplate).toHaveBeenCalledWith(offer.id, {
      priceDetail: 'bla bla bla',
    })
  })
})
