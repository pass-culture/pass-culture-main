import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'
import { beforeEach, expect } from 'vitest'

import { api } from '@/apiClient/api'
import { OfferStatus } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { defaultCollectiveTemplateOffer } from '@/commons/utils/factories/adageFactories'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import {
  IndividualOffersActionsBar,
  type IndividualOffersActionsBarProps,
} from './IndividualOffersActionsBar'

const renderActionsBar = (
  props: IndividualOffersActionsBarProps,
  overrides: RenderWithProvidersOptions = {}
) => {
  overrides.initialRouterEntries = ['/offres']
  renderWithProviders(
    <>
      <IndividualOffersActionsBar {...props} />
      <SnackBarContainer />
    </>,
    {
      storeOverrides: {
        offerer: {
          currentOfferer: { ...defaultGetOffererResponseModel, id: 1 },
        },
      },
      ...overrides,
    }
  )
}

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: vi.fn(),
}))

vi.mock('@/apiClient/api', () => ({
  api: {
    patchOffersActiveStatus: vi.fn(),
    deleteDraftOffers: vi.fn(),
    patchAllOffersActiveStatus: vi.fn(),
  },
}))

const defaultUseLocationValue = {
  state: { offer: defaultCollectiveTemplateOffer },
  hash: '',
  key: '',
  pathname: '/offres',
  search: '',
}

const mockLogEvent = vi.fn()

describe('ActionsBar', () => {
  let props: IndividualOffersActionsBarProps
  const offerIds = [
    { id: 1, status: OfferStatus.ACTIVE },
    { id: 2, status: OfferStatus.ACTIVE },
  ]

  beforeEach(() => {
    props = {
      canDelete: true,
      canPublish: true,
      canDeactivate: true,
      selectedOffers: offerIds,
      clearSelectedOffers: vi.fn(),
      areAllOffersSelected: false,
    }
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(router, 'useLocation').mockReturnValue(defaultUseLocationValue)
    vi.spyOn(api, 'patchAllOffersActiveStatus').mockResolvedValue({})
  })

  it('should have buttons to activate and deactivate offers, to delete, and to abort action', () => {
    renderActionsBar(props)

    expect(screen.getByRole('button', { name: 'Publier' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Mettre en pause' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Supprimer' })
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
  })

  it('should say how many offers are selected when only 1 offer is selected', () => {
    props.selectedOffers = [{ id: 1, status: OfferStatus.ACTIVE }]

    renderActionsBar(props)

    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
    renderActionsBar(props)

    expect(screen.queryByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  it('should show a generic count when more than 500 offers are selected', () => {
    props.selectedOffers = Array(101)
      .fill(null)
      .map((_val, i) => ({ id: i, status: OfferStatus.ACTIVE }))

    renderActionsBar(props)

    expect(screen.queryByText('100+ offres sélectionnées')).toBeInTheDocument()
  })

  it('should activate selected offers upon publication', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        { id: 1, status: OfferStatus.INACTIVE },
        { id: 2, status: OfferStatus.INACTIVE },
        { id: 3, status: OfferStatus.DRAFT },
      ],
    })

    await userEvent.click(screen.getByText('Publier'))

    expect(api.patchOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: true,
    })
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('2 offres ont bien été publiées')
    ).toBeInTheDocument()
  })

  it('should delete selected draft offers upon deletion', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        { id: 1, status: OfferStatus.DRAFT },
        { id: 2, status: OfferStatus.DRAFT },
      ],
    })

    await userEvent.click(screen.getByText('Supprimer'))
    await userEvent.click(screen.getByText('Supprimer ces brouillons'))

    expect(api.deleteDraftOffers).toHaveBeenLastCalledWith({
      ids: [1, 2],
    })
    expect(api.deleteDraftOffers).toHaveBeenCalledTimes(1)
    expect(api.deleteDraftOffers).toHaveBeenNthCalledWith(1, {
      ids: [1, 2],
    })
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('2 brouillons ont bien été supprimés')
    ).toBeInTheDocument()
  })

  it('should deactivate selected offers', async () => {
    renderActionsBar({
      ...props,
      areAllOffersSelected: false,
      selectedOffers: [
        { id: 1, status: OfferStatus.ACTIVE },
        { id: 2, status: OfferStatus.SOLD_OUT },
        { id: 3, status: OfferStatus.EXPIRED },
        { id: 4, status: OfferStatus.DRAFT },
        { id: 5, status: OfferStatus.INACTIVE },
      ],
    })

    await userEvent.click(screen.getByText('Mettre en pause'))
    const confirmDeactivateButton = screen.getAllByText('Mettre en pause')[1]
    await userEvent.click(confirmDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DISABLED_SELECTED_OFFERS,
      {
        from: '/offres',
        has_selected_all_offers: false,
      }
    )
    expect(api.patchOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: [1, 2, 3],
      isActive: false,
    })
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)

    expect(
      screen.getByText('3 offres ont bien été mises en pause')
    ).toBeInTheDocument()
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', async () => {
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Annuler'))

    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
  })

  it('should activate all offers on click on "Publier" button when all offers are selected', async () => {
    props.areAllOffersSelected = true
    renderActionsBar(props)

    const expectedBody = {
      categoryId: null,
      creationMode: null,
      isActive: true,
      nameOrIsbn: null,
      offererAddressId: null,
      offererId: 1,
      periodBeginningDate: null,
      periodEndingDate: null,
      status: null,
      venueId: null,
    }

    const activateButton = screen.getByText('Publier')
    await userEvent.click(activateButton)

    expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
      expectedBody
    )
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
  })

  it('should deactivate all offers on click on "Mettre en pause" button when all offers are selected', async () => {
    props.areAllOffersSelected = true
    renderActionsBar(props)

    const expectedBody = {
      categoryId: null,
      creationMode: null,
      isActive: false,
      nameOrIsbn: null,
      offererAddressId: null,
      offererId: 1,
      periodBeginningDate: null,
      periodEndingDate: null,
      status: null,
      venueId: null,
    }

    const deactivateButton = screen.getByText('Mettre en pause')
    await userEvent.click(deactivateButton)
    const confirmDeactivateButton = screen.getAllByText('Mettre en pause')[1]
    await userEvent.click(confirmDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DISABLED_SELECTED_OFFERS,
      {
        from: '/offres',
        has_selected_all_offers: true,
      }
    )
    expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
      expectedBody
    )
    expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
  })

  it('should track cancel all offers on click on "Annuler" button', async () => {
    props.areAllOffersSelected = true
    renderActionsBar(props)
    const deactivateButton = screen.getByText('Mettre en pause')

    await userEvent.click(deactivateButton)
    const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
    await userEvent.click(cancelDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_CANCELED_SELECTED_OFFERS,
      {
        from: '/offres',
        has_selected_all_offers: true,
      }
    )
  })

  it('should track cancel offer on click on "Annuler" button', async () => {
    props.areAllOffersSelected = false
    renderActionsBar(props)
    const deactivateButton = screen.getByText('Mettre en pause')

    await userEvent.click(deactivateButton)
    const cancelDeactivateButton = screen.getAllByText('Annuler')[1]
    await userEvent.click(cancelDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_CANCELED_SELECTED_OFFERS,
      {
        from: '/offres',
        has_selected_all_offers: false,
      }
    )
  })

  it('should show an error message when an error occurs after clicking on "Publier" button when all offers are selected', async () => {
    props.areAllOffersSelected = true
    vi.spyOn(api, 'patchAllOffersActiveStatus').mockRejectedValueOnce(null)
    renderActionsBar(props)

    const activateButton = screen.getByText('Publier')
    await userEvent.click(activateButton)

    expect(
      screen.getByText(
        'Une erreur est survenue lors de l’activation des offres'
      )
    ).toBeInTheDocument()
  })

  it('should show an error message when an error occurs after clicking on "Publier" button when some offers are selected', async () => {
    vi.spyOn(api, 'patchOffersActiveStatus').mockRejectedValueOnce(null)
    renderActionsBar(props)

    const activateButton = screen.getByText('Publier')
    await userEvent.click(activateButton)

    expect(
      screen.getByText(
        'Une erreur est survenue lors de l’activation des offres'
      )
    ).toBeInTheDocument()
  })

  it('should show an error message when an error occurs after clicking on "Supprimer" button when some offers are selected', async () => {
    vi.spyOn(api, 'deleteDraftOffers').mockRejectedValueOnce(null)
    renderActionsBar(props)

    const activateButton = screen.getByText('Supprimer')
    await userEvent.click(activateButton)

    await userEvent.click(screen.getByText('Supprimer ces brouillons'))

    expect(
      screen.getByText(
        'Une erreur est survenue lors de la suppression des brouillon'
      )
    ).toBeInTheDocument()
  })

  it('should not display actions when selected offers have the wrong status', () => {
    props.canDeactivate = false
    props.canPublish = false
    props.canDelete = false

    renderActionsBar(props)

    expect(screen.queryByText('Supprimer')).not.toBeInTheDocument()
    expect(screen.queryByText('Publier')).not.toBeInTheDocument()
    expect(screen.queryByText('Mettre en pause')).not.toBeInTheDocument()
  })

  describe('OA feature flag', () => {
    it('should make the right api call without OA FF', async () => {
      defaultUseLocationValue.search = 'offererAddressId=814'
      vi.spyOn(router, 'useLocation').mockReturnValueOnce(
        defaultUseLocationValue
      )

      props.areAllOffersSelected = true
      renderActionsBar(props)

      const expectedBody = {
        categoryId: null,
        creationMode: null,
        isActive: true,
        nameOrIsbn: null,
        offererAddressId: 814,
        offererId: 1,
        periodBeginningDate: null,
        periodEndingDate: null,
        status: null,
        venueId: null,
      }

      const activateButton = screen.getByText('Publier')
      await userEvent.click(activateButton)

      expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
        expectedBody
      )
      expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
    })

    it('should make the right api call with OA FF', async () => {
      defaultUseLocationValue.search = 'venueId=123'
      vi.spyOn(router, 'useLocation').mockReturnValueOnce(
        defaultUseLocationValue
      )
      props.areAllOffersSelected = true
      renderActionsBar(props)

      const expectedBody = {
        categoryId: null,
        creationMode: null,
        isActive: true,
        nameOrIsbn: null,
        offererAddressId: null,
        offererId: 1,
        periodBeginningDate: null,
        periodEndingDate: null,
        status: null,
        venueId: 123,
      }

      const activateButton = screen.getByText('Publier')
      await userEvent.click(activateButton)

      expect(api.patchAllOffersActiveStatus).toHaveBeenLastCalledWith(
        expectedBody
      )
      expect(props.clearSelectedOffers).toHaveBeenCalledTimes(1)
    })
  })
})
