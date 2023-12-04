import { screen } from '@testing-library/react'
import * as router from 'react-router-dom'

import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffersInfos } from '../OffersInfos'

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useLocation: vi.fn(),
}))

const renderOffersInfos = () => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <OffersInfos />
    </AdageUserContextProvider>
  )
}

describe('OffersInfos', () => {
  beforeEach(() => {
    vi.spyOn(router, 'useLocation').mockReturnValue({
      pathname: '',
      search: '',
      hash: '',
      state: { offer: defaultCollectiveTemplateOffer },
      key: 's',
    })
  })
  it('should display offers informations', () => {
    renderOffersInfos()

    expect(
      screen.getByRole('heading', { name: 'Mon offre vitrine' })
    ).toBeInTheDocument()
  })

  it('should display the breadcrumb with a link back to the discovery home', () => {
    renderOffersInfos()

    expect(screen.getByRole('link', { name: 'Découvrir' })).toBeInTheDocument()
  })
})
