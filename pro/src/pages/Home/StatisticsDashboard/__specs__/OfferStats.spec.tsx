import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { defaultGetOffererResponseModel } from 'utils/apiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OfferStats, OfferStatsProps } from '../OfferStats'

vi.mock('apiClient/api', () => ({
  api: {
    getOffererV2Stats: vi.fn(),
  },
}))

const renderOfferStats = (props: Partial<OfferStatsProps> = {}) =>
  renderWithProviders(
    <OfferStats
      offerer={{ ...defaultGetOffererResponseModel, isValidated: true }}
      {...props}
    />
  )

describe('OfferStats', () => {
  it('should render empty state when 0 everywhere', async () => {
    vi.spyOn(api, 'getOffererV2Stats').mockResolvedValueOnce({
      publishedPublicOffers: 0,
      publishedEducationalOffers: 0,
      pendingPublicOffers: 0,
      pendingEducationalOffers: 0,
    })

    renderOfferStats()

    expect(screen.getByText('Vos offres publiées')).toBeInTheDocument()
    expect(screen.queryByText('Vos offres en attente')).not.toBeInTheDocument()
    const individualOffers = await screen.findByText(
      'à destination du grand public'
    )
    expect(individualOffers.textContent).toContain(
      '0 à destination du grand public'
    )
    const collectiveOffers = await screen.findByText(
      'à destination de groupes scolaires'
    )
    expect(collectiveOffers.textContent).toContain(
      '0 à destination de groupes scolaires'
    )
  })

  it('should render stats when above 0', async () => {
    vi.spyOn(api, 'getOffererV2Stats').mockResolvedValueOnce({
      publishedPublicOffers: 10,
      publishedEducationalOffers: 0,
      pendingPublicOffers: 0,
      pendingEducationalOffers: 5,
    })

    renderOfferStats()

    expect(screen.getByText('Vos offres publiées')).toBeInTheDocument()
    expect(screen.queryByText('Vos offres en attente')).not.toBeInTheDocument()
    const individualOffers = await screen.findByText(
      'à destination du grand public'
    )
    expect(individualOffers.textContent).toContain(
      '10 à destination du grand public'
    )
    const collectiveOffers = await screen.findByText(
      'à destination de groupes scolaires'
    )
    expect(collectiveOffers.textContent).toContain(
      '0 à destination de groupes scolaires'
    )

    // TODO add pending offers
  })
})
