import { render, screen } from '@testing-library/react'
import React from 'react'

import { getCollectiveOfferTemplateFactory } from 'utils/collectiveApiFactories'

import CollectiveOfferPriceSection from '../CollectiveOfferPriceSection'

describe('CollectiveOfferPriceSection', () => {
  it('should display the price detail', async () => {
    render(
      <CollectiveOfferPriceSection
        offer={{
          ...getCollectiveOfferTemplateFactory(),
          educationalPriceDetail: 'Le détail du prix',
        }}
      />
    )
    expect(await screen.findByText('Prix')).toBeInTheDocument()
    expect(screen.getByText('Le détail du prix')).toBeInTheDocument()
  })
})
