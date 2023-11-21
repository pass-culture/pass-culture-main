import { screen } from '@testing-library/react'

import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffersInfos } from '../OffersInfos'

const renderOffersInfos = () => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <OffersInfos />
    </AdageUserContextProvider>
  )
}

describe('OffersInfos', () => {
  it('should display offers informations', () => {
    renderOffersInfos()

    expect(
      screen.getByRole('heading', { name: 'Une chouette à la mer' })
    ).toBeInTheDocument()
  })

  it('should display the breadcrumb with a link back to the discovery home', () => {
    renderOffersInfos()

    expect(screen.getByRole('link', { name: 'Découvrir' })).toBeInTheDocument()
  })
})
