import { screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
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
    const publishedIndividualOffers = await screen.findByText(
      'Voir les offres individuelles publiées'
    )
    expect(publishedIndividualOffers.parentElement?.textContent).toContain(
      '0 à destination du grand public'
    )
    const publishedCollectiveOffers = await screen.findByText(
      'Voir les offres collectives publiées'
    )
    expect(publishedCollectiveOffers.parentElement?.textContent).toContain(
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
    const publishedIndividualOffers = await screen.findByText(
      'Voir les offres individuelles publiées'
    )
    expect(publishedIndividualOffers.parentElement?.textContent).toContain(
      '10 à destination du grand public'
    )
    const publishedCollectiveOffers = await screen.findByText(
      'Voir les offres collectives publiées'
    )
    expect(publishedCollectiveOffers.parentElement?.textContent).toContain(
      '0 à destination de groupes scolaires'
    )

    const pendingIndividualOffers = await screen.findByText(
      'Voir les offres individuelles en attente'
    )
    expect(pendingIndividualOffers.parentElement?.textContent).toContain(
      '0 à destination du grand public'
    )
    const pendingCollectiveOffers = await screen.findByText(
      'Voir les offres collectives en attente'
    )
    expect(pendingCollectiveOffers.parentElement?.textContent).toContain(
      '5 à destination de groupes scolaires'
    )
  })

  it('should render when the count is too high', async () => {
    vi.spyOn(api, 'getOffererV2Stats').mockResolvedValueOnce({
      publishedPublicOffers: 500,
      publishedEducationalOffers: 0,
      pendingPublicOffers: 0,
      pendingEducationalOffers: 0,
    })

    renderOfferStats()

    expect(await screen.findByText('500+')).toBeInTheDocument()
  })
})
