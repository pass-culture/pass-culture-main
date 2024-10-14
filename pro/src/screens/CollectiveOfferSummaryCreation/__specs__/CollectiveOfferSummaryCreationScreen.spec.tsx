import { screen } from '@testing-library/react'

import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'commons/utils/collectiveApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { CollectiveOfferSummaryCreationScreen } from '../CollectiveOfferSummaryCreationScreen'

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
