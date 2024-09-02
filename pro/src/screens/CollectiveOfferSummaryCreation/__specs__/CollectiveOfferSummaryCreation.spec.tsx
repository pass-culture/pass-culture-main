import { screen } from '@testing-library/react'

import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferSummaryCreationScreen } from '../CollectiveOfferSummaryCreation'

describe('CollectiveOfferSummaryCreationScreen', () => {
  it('should render bookable offer summary creation screen with three edit links (details, stock, institution)', () => {
    renderWithProviders(
      <CollectiveOfferSummaryCreationScreen
        offer={getCollectiveOfferFactory()}
      />
    )

    expect(screen.getAllByText('Modifier')).toHaveLength(3)
  })

  it('should render template offer summary creation screen with one edit link', () => {
    renderWithProviders(
      <CollectiveOfferSummaryCreationScreen
        offer={getCollectiveOfferTemplateFactory()}
      />
    )

    expect(screen.getAllByText('Modifier')).toHaveLength(1)
  })
})
