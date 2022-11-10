import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'

import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
  collectiveStockFactory,
} from 'utils/collectiveApiFactories'

import CollectiveOfferPracticalInformation from '..'

describe('CollectiveOfferPracticalInformation', () => {
  it('when offer is template', () => {
    render(
      <CollectiveOfferPracticalInformation
        offer={collectiveOfferTemplateFactory({
          educationalPriceDetail: 'Le détail du prix',
        })}
      />
    )

    const priceDetail = screen.getByText(/Informations sur le prix/)
    expect(priceDetail).toBeInTheDocument()
    expect(screen.getByText('Le détail du prix')).toBeInTheDocument()
  })

  it('when offer is not template', () => {
    render(
      <CollectiveOfferPracticalInformation
        offer={collectiveOfferFactory(
          {},
          collectiveStockFactory({
            educationalPriceDetail: 'Le détail du prix',
          })
        )}
      />
    )

    const priceDetail = screen.queryByText(/Informations sur le prix/)
    expect(priceDetail).not.toBeInTheDocument()
    expect(screen.queryByText('Le détail du prix')).not.toBeInTheDocument()
  })
})
