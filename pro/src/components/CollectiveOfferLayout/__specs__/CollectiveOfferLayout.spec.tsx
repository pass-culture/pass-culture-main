import '@testing-library/jest-dom'
import { screen } from '@testing-library/react'
import React from 'react'
import * as router from 'react-router-dom'

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: jest.fn(),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getCollectiveOffer: jest.fn(),
    getCollectiveOfferTemplate: jest.fn(),
  },
}))

import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferLayout from '../CollectiveOfferLayout'

const renderCollectiveOfferLayout = (
  path: string,
  isFromTemplate?: boolean
) => {
  renderWithProviders(
    <CollectiveOfferLayout
      subTitle="Ma super offre"
      isFromTemplate={isFromTemplate}
    >
      Test
    </CollectiveOfferLayout>,
    { initialRouterEntries: [path] }
  )
}

describe('CollectiveOfferLayout', () => {
  it('should render subtitle if provided', () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: 'A1' })
    renderCollectiveOfferLayout('/offre/A1/collectif/edition')

    const offersubTitle = screen.getByText('Ma super offre')
    const tagOfferTemplate = screen.queryByText('Offre vitrine')

    expect(offersubTitle).toBeInTheDocument()
    expect(tagOfferTemplate).not.toBeInTheDocument()
  })
  it("should render 'Offre vitrine' tag if offer is template", () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: 'T-A1' })
    renderCollectiveOfferLayout('/offre/T-A1/collectif/edition')

    const tagOfferTemplate = screen.getByText('Offre vitrine')

    expect(tagOfferTemplate).toBeInTheDocument()
  })
  it('should render summary page layout in edition', () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: 'A1' })
    renderCollectiveOfferLayout('/offre/A1/collectif/recapitulatif')

    const title = screen.getByRole('heading', { name: 'Récapitulatif' })

    expect(title).toBeInTheDocument()
  })
  it('should display creation title', () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: 'A1' })
    renderCollectiveOfferLayout('/offre/A1/collectif/')

    const title = screen.getByRole('heading', {
      name: 'Créer une nouvelle offre collective',
    })

    expect(title).toBeInTheDocument()
  })
  it('should display creation from template title', () => {
    jest.spyOn(router, 'useParams').mockReturnValue({ offerId: 'A1' })
    renderCollectiveOfferLayout('/offre/A1/collectif/', true)

    const title = screen.getByRole('heading', {
      name: 'Créer une offre pour un établissement scolaire',
    })

    expect(title).toBeInTheDocument()
  })
})
