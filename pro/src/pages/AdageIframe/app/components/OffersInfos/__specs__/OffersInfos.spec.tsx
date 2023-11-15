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

    expect(screen.getByText('Une chouette à la mer')).toBeInTheDocument()
  })
})
