import { screen } from '@testing-library/react'

import { getCollectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferPriceSection } from '../CollectiveOfferPriceSection'

describe('CollectiveOfferPriceSection', () => {
  it('should display the price detail', async () => {
    renderWithProviders(
      <CollectiveOfferPriceSection
        offer={{
          ...getCollectiveOfferTemplateFactory(),
          priceDetail: 'Le détail du prix',
        }}
      />
    )
    expect(await screen.findByText('Prix')).toBeVisible()
    expect(screen.getByText('Le détail du prix')).toBeVisible()
  })
})
