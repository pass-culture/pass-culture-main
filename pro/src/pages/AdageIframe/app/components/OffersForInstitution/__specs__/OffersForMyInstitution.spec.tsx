import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import React from 'react'

import { apiAdage } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser, defaultCollectiveOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffersForMyInstitution } from '../OffersForMyInstitution'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getCollectiveOffersForMyInstitution: vi.fn(),
  },
}))

const renderOffersForMyInstitution = (
  user = defaultAdageUser,
  features?: string[]
) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <OffersForMyInstitution />
    </AdageUserContextProvider>,
    { features: features }
  )
}

describe('OffersInstitutionList', () => {
  it('should display no result page', async () => {
    vi.spyOn(
      apiAdage,
      'getCollectiveOffersForMyInstitution'
    ).mockResolvedValueOnce({ collectiveOffers: [] })

    renderOffersForMyInstitution({ ...defaultAdageUser, offersCount: 0 })

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByText('Vous n’avez pas d’offre à préréserver')
    ).toBeInTheDocument()
  })

  it('should display list of offers for my institution', async () => {
    vi.spyOn(
      apiAdage,
      'getCollectiveOffersForMyInstitution'
    ).mockResolvedValueOnce({ collectiveOffers: [defaultCollectiveOffer] })

    renderOffersForMyInstitution()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText(defaultCollectiveOffer.name)).toBeInTheDocument()
  })

  it('should display title and banner', async () => {
    renderOffersForMyInstitution()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByText('Pour mon établissement'))
    expect(
      screen.getByRole('link', {
        name: /Voir la page “Suivi pass Culture”/i,
      })
    ).toHaveAttribute('href', 'adage/passculture/index')
  })

  it('should show an offer card', async () => {
    vi.spyOn(
      apiAdage,
      'getCollectiveOffersForMyInstitution'
    ).mockResolvedValueOnce({ collectiveOffers: [defaultCollectiveOffer] })

    renderOffersForMyInstitution(defaultAdageUser)

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    expect(
      screen.getByRole('link', { name: defaultCollectiveOffer.name })
    ).toBeInTheDocument()
  })
})
