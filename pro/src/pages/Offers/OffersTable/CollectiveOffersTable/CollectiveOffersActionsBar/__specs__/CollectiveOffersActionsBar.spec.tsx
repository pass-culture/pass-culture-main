import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  CollectiveBookingStatus,
  CollectiveOfferStatus,
  CollectiveOffersStockResponseModel,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Notification } from 'components/Notification/Notification'
import { Events } from 'core/FirebaseEvents/constants'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  CollectiveOffersActionsBar,
  CollectiveOffersActionsBarProps,
} from '../CollectiveOffersActionsBar'

const renderActionsBar = (props: CollectiveOffersActionsBarProps) => {
  renderWithProviders(
    <>
      <CollectiveOffersActionsBar {...props} />
      <Notification />
    </>,
    { storeOverrides: {}, initialRouterEntries: ['/offres/collectives'] }
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    patchCollectiveOffersActiveStatus: vi.fn(),
    patchCollectiveOffersTemplateActiveStatus: vi.fn(),
    patchAllCollectiveOffersActiveStatus: vi.fn(),
    patchCollectiveOffersTemplateArchive: vi.fn(),
    patchCollectiveOffersArchive: vi.fn(),
  },
}))

const mockLogEvent = vi.fn()
const mockGetUpdateOffersStatusMessage = vi.fn()

describe('ActionsBar', () => {
  let props: CollectiveOffersActionsBarProps
  const offerIds = [1, 2]
  let stocks: Array<CollectiveOffersStockResponseModel>

  beforeEach(() => {
    stocks = [
      {
        beginningDatetime: String(new Date()),
        hasBookingLimitDatetimePassed: true,
        remainingQuantity: 1,
      },
    ]
    props = {
      getUpdateOffersStatusMessage: mockGetUpdateOffersStatusMessage,
      selectedOffers: offerIds.map((offerId) => ({
        ...collectiveOfferFactory(),
        id: offerId,
      })),
      clearSelectedOfferIds: vi.fn(),
      toggleSelectAllCheckboxes: vi.fn(),
      areAllOffersSelected: false,
    }
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should have buttons to unckeck, disable and publish offers', () => {
    renderActionsBar(props)

    expect(
      screen.queryByText('Publier', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Masquer', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.queryByText('Annuler', { selector: 'button' })
    ).toBeInTheDocument()
  })

  it('should say how many offers are selected when only 1 offer is selected', () => {
    props.selectedOffers = [collectiveOfferFactory()]

    renderActionsBar(props)

    expect(screen.queryByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
    renderActionsBar(props)

    expect(screen.queryByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  it('should show a generic count when more than 500 offers are selected', () => {
    props.selectedOffers = Array(501)
      .fill(null)
      .map((val, i) => ({ ...collectiveOfferFactory(), id: i }))

    renderActionsBar(props)

    expect(screen.queryByText('500+ offres sélectionnées')).toBeInTheDocument()
  })

  it('should activate selected offers upon publication', async () => {
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Publier'))

    expect(api.patchCollectiveOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: true,
    })
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
    expect(
      screen.getByText('2 offres ont bien été publiées')
    ).toBeInTheDocument()
  })

  it('should not activate offers when a draft is selected', async () => {
    mockGetUpdateOffersStatusMessage.mockReturnValueOnce(
      'Vous ne pouvez pas publier des brouillons depuis cette liste'
    )

    renderActionsBar(props)

    await userEvent.click(screen.getByText('Publier'))

    expect(api.patchCollectiveOffersActiveStatus).not.toHaveBeenCalled()
    expect(props.clearSelectedOfferIds).not.toHaveBeenCalled()
    expect(
      screen.getByText(
        'Vous ne pouvez pas publier des brouillons depuis cette liste'
      )
    ).toBeInTheDocument()
  })

  it('should deactivate selected offers', async () => {
    props.areAllOffersSelected = false
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Masquer'))
    const confirmDeactivateButton = screen.getAllByText('Masquer')[1]!
    await userEvent.click(confirmDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DISABLED_SELECTED_OFFERS,
      {
        from: '/offres/collectives',
        has_selected_all_offers: false,
      }
    )
    expect(api.patchCollectiveOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: false,
    })
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)

    expect(
      screen.getByText('2 offres ont bien été masquées')
    ).toBeInTheDocument()
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', async () => {
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Annuler'))

    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
  })

  it('should activate all offers on click on "Publier" button when all offers are selected', async () => {
    props.areAllOffersSelected = true
    renderActionsBar(props)

    const expectedBody = {
      isActive: true,
    }

    const activateButton = screen.getByText('Publier')
    await userEvent.click(activateButton)

    expect(api.patchAllCollectiveOffersActiveStatus).toHaveBeenLastCalledWith(
      expectedBody
    )
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
  })

  it('should show an error message when an error occurs after clicking on "Publier" button when all offers are selected', async () => {
    props.areAllOffersSelected = true
    vi.spyOn(api, 'patchAllCollectiveOffersActiveStatus').mockRejectedValueOnce(
      null
    )
    renderActionsBar(props)

    const activateButton = screen.getByText('Publier')
    await userEvent.click(activateButton)

    expect(screen.getByText('Une erreur est survenue'))
  })

  it('should show an error message when an error occurs after clicking on "Publier" button when some offers are selected', async () => {
    vi.spyOn(api, 'patchCollectiveOffersActiveStatus').mockRejectedValueOnce(
      null
    )
    renderActionsBar(props)

    const activateButton = screen.getByText('Publier')
    await userEvent.click(activateButton)

    expect(screen.getByText('Une erreur est survenue'))
  })

  it('should deactivate all offers on click on "Masquer" button when all offers are selected', async () => {
    props.areAllOffersSelected = true
    renderActionsBar(props)

    const expectedBody = {
      isActive: false,
    }

    const deactivateButton = screen.getByText('Masquer')
    await userEvent.click(deactivateButton)
    const confirmDeactivateButton = screen.getAllByText('Masquer')[1]!
    await userEvent.click(confirmDeactivateButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DISABLED_SELECTED_OFFERS,
      {
        from: '/offres/collectives',
        has_selected_all_offers: true,
      }
    )
    expect(api.patchAllCollectiveOffersActiveStatus).toHaveBeenLastCalledWith(
      expectedBody
    )
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
  })

  it('should not deactivate offers on click on "Masquer" when at least one offer is not published or expired', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        collectiveOfferFactory({ id: 1, status: CollectiveOfferStatus.ACTIVE }),
        collectiveOfferFactory({
          id: 2,
          status: CollectiveOfferStatus.PENDING,
        }),
      ],
    })

    const deactivateButton = screen.getByText('Masquer')
    await userEvent.click(deactivateButton)

    expect(
      screen.getByText(
        'Seules les offres au statut publié ou expiré peuvent être masquées.'
      )
    ).toBeInTheDocument()
  })

  it('should not deactivate offers on click on "Masquer" when at least one offer expired but with booking finished', async () => {
    const expiredOffer = collectiveOfferFactory({
      id: 1,
      status: CollectiveOfferStatus.EXPIRED,
    })
    renderActionsBar({
      ...props,
      selectedOffers: [
        {
          ...expiredOffer,
          booking: {
            booking_status: CollectiveBookingStatus.REIMBURSED,
            id: 3,
          },
        },
        collectiveOfferFactory({ id: 2, status: CollectiveOfferStatus.ACTIVE }),
      ],
    })

    const deactivateButton = screen.getByText('Masquer')
    await userEvent.click(deactivateButton)

    expect(
      screen.getByText(
        'Seules les offres au statut publié ou expiré peuvent être masquées.'
      )
    ).toBeInTheDocument()
  })

  it('should only make one call if the ids all come from the bookable offer', async () => {
    renderActionsBar({
      ...props,
      areAllOffersSelected: false,
      selectedOffers: [
        collectiveOfferFactory({ id: 1, status: CollectiveOfferStatus.ACTIVE }),
        collectiveOfferFactory({ id: 2, status: CollectiveOfferStatus.ACTIVE }),
      ],
    })

    await userEvent.click(screen.getByText('Masquer'))
    const confirmDeactivateButton = screen.getAllByText('Masquer')[1]!
    await userEvent.click(confirmDeactivateButton)

    expect(api.patchCollectiveOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: false,
    })

    expect(api.patchCollectiveOffersTemplateActiveStatus).toHaveBeenCalledTimes(
      0
    )
  })

  it('should only make one call if the ids all come from template offer', async () => {
    renderActionsBar({
      ...props,
      areAllOffersSelected: false,
      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          status: CollectiveOfferStatus.ACTIVE,
          isShowcase: true,
        }),
        collectiveOfferFactory({
          id: 2,
          status: CollectiveOfferStatus.ACTIVE,
          isShowcase: true,
        }),
      ],
    })

    await userEvent.click(screen.getByText('Masquer'))
    const confirmDeactivateButton = screen.getAllByText('Masquer')[1]!
    await userEvent.click(confirmDeactivateButton)

    expect(
      api.patchCollectiveOffersTemplateActiveStatus
    ).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: false,
    })

    expect(api.patchCollectiveOffersActiveStatus).toHaveBeenCalledTimes(0)
  })

  it('should make two calls if the ids come from template offer and bookable offer', async () => {
    renderActionsBar({
      ...props,
      areAllOffersSelected: false,
      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          status: CollectiveOfferStatus.ACTIVE,
          isShowcase: true,
        }),
        collectiveOfferFactory({
          id: 2,
          status: CollectiveOfferStatus.ACTIVE,
          isShowcase: true,
        }),
        collectiveOfferFactory({
          id: 3,
          status: CollectiveOfferStatus.ACTIVE,
        }),
      ],
    })

    await userEvent.click(screen.getByText('Masquer'))
    const confirmDeactivateButton = screen.getAllByText('Masquer')[1]!
    await userEvent.click(confirmDeactivateButton)

    expect(
      api.patchCollectiveOffersTemplateActiveStatus
    ).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: false,
    })

    expect(api.patchCollectiveOffersActiveStatus).toHaveBeenLastCalledWith({
      ids: [3],
      isActive: false,
    })
  })

  it('should archive offers on click on "Archiver"', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          status: CollectiveOfferStatus.ACTIVE,
          stocks,
        }),
        collectiveOfferFactory({
          id: 2,
          status: CollectiveOfferStatus.ACTIVE,
          stocks,
          isShowcase: true,
        }),
      ],
    })

    const archivingButton = screen.getByText('Archiver')
    await userEvent.click(archivingButton)

    const confirmArchivingButton = screen.getByText('Archiver les offres')
    await userEvent.click(confirmArchivingButton)

    expect(api.patchCollectiveOffersTemplateArchive).toHaveBeenLastCalledWith({
      ids: [2],
    })

    expect(api.patchCollectiveOffersArchive).toHaveBeenLastCalledWith({
      ids: [1],
    })

    expect(
      screen.getByText('2 offres ont bien été archivée')
    ).toBeInTheDocument()
  })

  it('should not archive offers on click on "Archiver" when at least one offer cannot be archived', async () => {
    renderActionsBar({
      ...props,

      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          status: CollectiveOfferStatus.ACTIVE,
          stocks,
        }),
        collectiveOfferFactory({
          id: 2,
          status: CollectiveOfferStatus.PENDING,
          stocks,
        }),
      ],
    })

    const archivingButton = screen.getByText('Archiver')
    await userEvent.click(archivingButton)

    expect(
      screen.getByText(
        'Les offres liées à des réservations en cours ne peuvent pas être archivées'
      )
    ).toBeInTheDocument()
  })
})
