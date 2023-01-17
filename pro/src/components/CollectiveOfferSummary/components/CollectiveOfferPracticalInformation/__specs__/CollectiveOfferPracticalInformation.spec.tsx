import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import React from 'react'
import { Provider } from 'react-redux'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'
import { configureTestStore } from 'store/testUtils'
import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
  collectiveStockFactory,
} from 'utils/collectiveApiFactories'

import CollectiveOfferPracticalInformation from '..'

jest.mock('apiClient/api', () => ({
  api: {
    getVenue: jest.fn(),
  },
}))

describe('CollectiveOfferPracticalInformation', () => {
  it('when offer is template', async () => {
    jest.spyOn(api, 'getVenue').mockResolvedValue({
      id: 'AE',
    } as GetVenueResponseModel)
    const store = configureTestStore()
    render(
      <Provider store={store}>
        <CollectiveOfferPracticalInformation
          offer={collectiveOfferTemplateFactory({
            educationalPriceDetail: 'Le détail du prix',
          })}
        />
      </Provider>
    )
    await waitFor(() => {
      expect(api.getVenue).toHaveBeenCalledTimes(1)
    })
    const priceDetail = screen.getByText(/Informations sur le prix/)
    expect(priceDetail).toBeInTheDocument()
    expect(screen.getByText('Le détail du prix')).toBeInTheDocument()
  })

  it('when offer is not template', () => {
    const store = configureTestStore()
    render(
      <Provider store={store}>
        <CollectiveOfferPracticalInformation
          offer={collectiveOfferFactory(
            {},
            collectiveStockFactory({
              educationalPriceDetail: 'Le détail du prix',
            })
          )}
        />
      </Provider>
    )

    const priceDetail = screen.queryByText(/Informations sur le prix/)
    expect(priceDetail).not.toBeInTheDocument()
    expect(screen.queryByText('Le détail du prix')).not.toBeInTheDocument()
  })
})
