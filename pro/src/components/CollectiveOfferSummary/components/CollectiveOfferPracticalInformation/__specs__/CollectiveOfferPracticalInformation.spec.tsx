import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'
import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
  collectiveStockFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferPracticalInformation from '..'

jest.mock('apiClient/api', () => ({
  api: {
    getVenue: jest.fn(),
  },
}))

describe('CollectiveOfferPracticalInformation', () => {
  it('when offer is template', async () => {
    jest.spyOn(api, 'getVenue').mockResolvedValue({
      nonHumanizedId: 1,
    } as GetVenueResponseModel)
    renderWithProviders(
      <CollectiveOfferPracticalInformation
        offer={collectiveOfferTemplateFactory({
          educationalPriceDetail: 'Le détail du prix',
        })}
      />
    )
    await waitFor(() => {
      expect(api.getVenue).toHaveBeenCalledTimes(1)
    })
    const priceDetail = await screen.findByText(/Informations sur le prix/)
    expect(priceDetail).toBeInTheDocument()
    expect(screen.getByText('Le détail du prix')).toBeInTheDocument()
  })

  it('when offer is not template', async () => {
    renderWithProviders(
      <CollectiveOfferPracticalInformation
        offer={collectiveOfferFactory(
          {},
          collectiveStockFactory({
            educationalPriceDetail: 'Le détail du prix',
          })
        )}
      />
    )
    await waitFor(() => {
      expect(api.getVenue).toHaveBeenCalledTimes(1)
    })

    const priceDetail = screen.queryByText(/Informations sur le prix/)
    expect(priceDetail).not.toBeInTheDocument()
    expect(screen.queryByText('Le détail du prix')).not.toBeInTheDocument()
  })
})
