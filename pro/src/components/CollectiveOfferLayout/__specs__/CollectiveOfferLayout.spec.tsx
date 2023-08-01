import '@testing-library/jest-dom'
import { screen } from '@testing-library/react'
import React from 'react'

vi.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferLayout, {
  CollectiveOfferLayoutProps,
} from '../CollectiveOfferLayout'

const renderCollectiveOfferLayout = (
  path: string,
  props: Partial<CollectiveOfferLayoutProps>
) => {
  renderWithProviders(
    <CollectiveOfferLayout subTitle="Ma super offre" {...props}>
      Test
    </CollectiveOfferLayout>,
    { initialRouterEntries: [path] }
  )
}

describe('CollectiveOfferLayout', () => {
  it('should render subtitle if provided', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/edition', {})

    const offersubTitle = screen.getByText('Ma super offre')
    const tagOfferTemplate = screen.queryByText('Offre vitrine')

    expect(offersubTitle).toBeInTheDocument()
    expect(tagOfferTemplate).not.toBeInTheDocument()
  })

  it("should render 'Offre vitrine' tag if offer is template", () => {
    renderCollectiveOfferLayout('/offre/T-A1/collectif/edition', {
      isTemplate: true,
    })

    const tagOfferTemplate = screen.getByText('Offre vitrine')

    expect(tagOfferTemplate).toBeInTheDocument()
  })

  it('should render summary page layout in edition', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/recapitulatif', {})

    const title = screen.getByRole('heading', { name: 'Récapitulatif' })

    expect(title).toBeInTheDocument()
  })

  it('should display creation title', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/', { isCreation: true })

    const title = screen.getByRole('heading', {
      name: 'Créer une nouvelle offre collective',
    })

    expect(title).toBeInTheDocument()
  })

  it('should display creation from template title', () => {
    renderCollectiveOfferLayout('/offre/A1/collectif/', {
      isFromTemplate: true,
      isCreation: true,
    })

    const title = screen.getByRole('heading', {
      name: 'Créer une offre pour un établissement scolaire',
    })

    expect(title).toBeInTheDocument()
  })
})
