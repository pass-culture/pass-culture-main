import { screen } from '@testing-library/react'
import * as router from 'react-router'

import { api } from '@/apiClient//api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseIdModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient//v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import * as useNotification from '@/commons/hooks/useNotification'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  CollectiveCreationOfferNavigation,
  CollectiveCreationOfferNavigationProps,
  CollectiveOfferStep,
} from '../CollectiveCreationOfferNavigation'

const renderCollectiveOfferNavigation = (
  props: CollectiveCreationOfferNavigationProps,
  options?: RenderWithProvidersOptions
) =>
  renderWithProviders(<CollectiveCreationOfferNavigation {...props} />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
      },
    },
    ...options,
  })

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: vi.fn(),
}))

describe('CollectiveCreationOfferNavigation', () => {
  let offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  let props: CollectiveCreationOfferNavigationProps
  const offerId = 1
  const mockLogEvent = vi.fn()
  const notifyError = vi.fn()
  const notifySuccess = vi.fn()
  const defaultUseLocationValue = {
    state: {},
    hash: '',
    key: '',
    pathname: '',
    search: '',
  }

  beforeEach(async () => {
    offer = getCollectiveOfferTemplateFactory({
      isTemplate: true,
    })
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValue(offer)

    vi.spyOn(api, 'getVenue').mockResolvedValue(defaultGetVenue)

    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValue(offer)

    vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [],
    })

    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])

    vi.spyOn(api, 'createCollectiveOffer').mockResolvedValue(
      {} as CollectiveOfferResponseIdModel
    )

    const notifsImport = (await vi.importActual(
      '@/commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
      success: notifySuccess,
    }))

    vi.spyOn(router, 'useLocation').mockReturnValue(defaultUseLocationValue)

    props = {
      activeStep: CollectiveOfferStep.DETAILS,
      offerId: offerId,
      isTemplate: false,
      offer: getCollectiveOfferFactory(),
    }
  })

  it('should display navigation for collective offer in creation', async () => {
    renderCollectiveOfferNavigation({ ...props, offerId: 0 })

    expect(screen.getByTestId('stepper')).toBeInTheDocument()

    const listItems = await screen.findAllByRole('listitem')

    expect(listItems).toHaveLength(5)
    expect(listItems[0]).toHaveTextContent('Détails de l’offre')
    expect(listItems[1]).toHaveTextContent('Dates et prix')
    expect(listItems[2]).toHaveTextContent('Établissement et enseignant')
    expect(listItems[3]).toHaveTextContent('Récapitulatif')
    expect(listItems[4]).toHaveTextContent('Aperçu')

    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(0)
  })

  it('should show different links if offer is template', async () => {
    renderCollectiveOfferNavigation({
      ...props,
      activeStep: CollectiveOfferStep.SUMMARY,
      offer: getCollectiveOfferFactory({
        institution: undefined,
        collectiveStock: undefined,
      }),
      isTemplate: true,
    })

    const listItems = await screen.findAllByRole('listitem')
    expect(listItems).toHaveLength(3)
    expect(screen.queryByText('Dates et prix')).not.toBeInTheDocument()
    expect(screen.queryByText('Visibilité')).not.toBeInTheDocument()

    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(1)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/vitrine/${offerId}/creation`
    )
  })

  it('should show links if stocks is the active step', () => {
    renderCollectiveOfferNavigation({
      ...props,
      activeStep: CollectiveOfferStep.STOCKS,
      offer: getCollectiveOfferFactory({
        institution: undefined,
        collectiveStock: undefined,
      }),
    })

    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(2)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
  })

  it('should show links if visibility is the active step', () => {
    renderCollectiveOfferNavigation({
      ...props,
      activeStep: CollectiveOfferStep.VISIBILITY,
      offer: getCollectiveOfferFactory({
        institution: undefined,
      }),
    })
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
    expect(links[2].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/visibilite`
    )
  })

  it('should show links if summary is the active step', () => {
    renderCollectiveOfferNavigation({
      ...props,
      activeStep: CollectiveOfferStep.SUMMARY,
      offer: getCollectiveOfferFactory({
        institution: {
          city: '',
          id: 1,
          institutionId: '2',
          name: '',
          phoneNumber: '',
          postalCode: '',
        },
      }),
    })
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(5)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
    expect(links[2].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/visibilite`
    )
    expect(links[3].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/creation/recapitulatif`
    )
    expect(links[4].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/creation/apercu`
    )
  })

  it('should show links if confirmation is the active step', () => {
    renderCollectiveOfferNavigation({
      ...props,
      activeStep: CollectiveOfferStep.CONFIRMATION,
      offer: getCollectiveOfferFactory({
        institution: {
          city: '',
          id: 1,
          institutionId: '2',
          name: '',
          phoneNumber: '',
          postalCode: '',
        },
      }),
    })
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(5)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offerId}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks`
    )
    expect(links[2].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/visibilite`
    )
    expect(links[3].getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/creation/recapitulatif`
    )
  })

  it('should show links if confirmation is the active step and the offer is template', () => {
    renderCollectiveOfferNavigation({
      ...props,
      activeStep: CollectiveOfferStep.CONFIRMATION,
      offer: getCollectiveOfferTemplateFactory(),
      isTemplate: true,
    })
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
  })

  it('should not show create bookable offer button if template offer has pending status', () => {
    renderCollectiveOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...offer,
        displayedStatus: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
      },
    })

    const duplicateOffer = screen.queryByRole('button', {
      name: 'Créer une offre réservable',
    })

    expect(duplicateOffer).not.toBeInTheDocument()
  })

  it('should be able to go to the visibility ans stocks step if the institurion and stock are already filled', () => {
    renderCollectiveOfferNavigation({
      ...props,
      offer: getCollectiveOfferFactory(),
      isTemplate: false,
      activeStep: CollectiveOfferStep.DETAILS,
    })

    expect(
      screen.getByRole('link', { name: /Établissement et enseignant/ })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: /Dates et prix/ })
    ).toBeInTheDocument()
  })

  it('should be able to go to the stocks step if the details are already filled', () => {
    renderCollectiveOfferNavigation({
      ...props,
      offer: getCollectiveOfferFactory({
        institution: undefined,
        collectiveStock: undefined,
      }),
      activeStep: CollectiveOfferStep.DETAILS,
    })

    expect(
      screen.queryByRole('link', { name: /Établissement et enseignant/ })
    ).not.toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: /Dates et prix/ })
    ).toBeInTheDocument()
  })
})
