import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import * as router from 'react-router-dom'

import { apiAdage } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OffersInfos } from '../OffersInfos'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

vi.mock('react-router-dom', async () => ({
  ...((await vi.importActual('react-router-dom')) ?? {}),
  useLocation: vi.fn(),
  useParams: () => ({
    offerId: '1',
  }),
}))

const renderOffersInfos = () => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <OffersInfos />
    </AdageUserContextProvider>
  )
}

const defaultUseLocationValue = {
  state: { offer: defaultCollectiveTemplateOffer },
  hash: '',
  key: '',
  pathname: '',
  search: '',
}

describe('OffersInfos', () => {
  beforeEach(() => {
    vi.spyOn(router, 'useLocation').mockReturnValue(defaultUseLocationValue)
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

  it('should display the offer that is passed through the router when the user navigates within the app', () => {
    renderOffersInfos()

    expect(
      screen.getByRole('heading', { name: defaultCollectiveTemplateOffer.name })
    ).toBeInTheDocument()
  })

  it('should fetch the offer with the id in the url when there is no offer in the router location', async () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      ...defaultUseLocationValue,
      state: { offer: null },
    })

    const fetchOfferSpy = vi
      .spyOn(apiAdage, 'getCollectiveOfferTemplate')
      .mockResolvedValueOnce(defaultCollectiveTemplateOffer)

    renderOffersInfos()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: defaultCollectiveTemplateOffer.name })
    ).toBeInTheDocument()

    expect(fetchOfferSpy).toHaveBeenCalledWith(1)
  })

  it('should show an error message when the offer had to be fetched but was not found', async () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      ...defaultUseLocationValue,
      state: { offer: null },
    })

    vi.spyOn(apiAdage, 'getCollectiveOfferTemplate').mockRejectedValueOnce(null)

    renderOffersInfos()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: 'Cette offre est introuvable' })
    ).toBeInTheDocument()
  })
})
