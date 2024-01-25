import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import * as router from 'react-router-dom'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OfferInfos } from '../OfferInfos'

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

const renderOfferInfos = (user: AuthenticatedResponse = defaultAdageUser) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={user}>
      <OfferInfos />
    </AdageUserContextProvider>
  )
}

const defaultUseLocationValue = {
  state: { offer: defaultCollectiveTemplateOffer },
  hash: '',
  key: '',
  pathname: '/adage-iframe/decouverte/offre/10',
  search: '',
}

describe('OfferInfos', () => {
  beforeEach(() => {
    vi.spyOn(router, 'useLocation').mockReturnValue(defaultUseLocationValue)
  })

  it('should display offers informations', () => {
    renderOfferInfos()

    expect(
      screen.getByRole('heading', { name: 'Mon offre vitrine' })
    ).toBeInTheDocument()
  })

  it('should display the breadcrumb with a link back to the discovery home', () => {
    renderOfferInfos()

    expect(screen.getByRole('link', { name: 'Découvrir' })).toHaveAttribute(
      'href',
      '/adage-iframe/decouverte?token=null'
    )
  })

  it("should display the breadcrumb with a link to the search page if the url doesn't contain a known parent page name", () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      ...defaultUseLocationValue,
      pathname: '',
    })

    renderOfferInfos()

    expect(screen.getByRole('link', { name: 'Recherche' })).toHaveAttribute(
      'href',
      '/adage-iframe/recherche?token=null'
    )
  })

  it("should display the breadcrumb with a link back to the search page if the url contains 'recherche'", () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      ...defaultUseLocationValue,
      pathname: '/adage-iframe/recherche/offre/10',
    })

    renderOfferInfos()

    expect(screen.getByRole('link', { name: 'Recherche' })).toHaveAttribute(
      'href',
      '/adage-iframe/recherche?token=null'
    )
  })

  it("should display the breadcrumb with a link back to the favorite page if the url contains 'mes-favoris'", () => {
    vi.spyOn(router, 'useLocation').mockReturnValueOnce({
      ...defaultUseLocationValue,
      pathname: '/adage-iframe/mes-favoris/offre/10',
    })

    renderOfferInfos()

    expect(screen.getByRole('link', { name: 'Mes favoris' })).toHaveAttribute(
      'href',
      '/adage-iframe/mes-favoris?token=null'
    )
  })

  it('should display the breadcrumb with a link back to the search page if the user is admin', () => {
    renderOfferInfos({ ...defaultAdageUser, role: AdageFrontRoles.READONLY })

    expect(screen.getByRole('link', { name: 'Recherche' })).toHaveAttribute(
      'href',
      '/adage-iframe/recherche?token=null'
    )
  })

  it('should display the offer that is passed through the router when the user navigates within the app', () => {
    renderOfferInfos()

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

    renderOfferInfos()

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('heading', { name: defaultCollectiveTemplateOffer.name })
    ).toBeInTheDocument()

    expect(fetchOfferSpy).toHaveBeenCalledWith(1)
  })
})
