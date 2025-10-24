import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import type {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import {
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  type CollectiveOffersStockResponseModel,
  CollectiveOfferTemplateAllowedAction,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import {
  CollectiveOffersActionsBar,
  type CollectiveOffersActionsBarProps,
} from '../CollectiveOffersActionsBar'

const renderActionsBar = (
  props: CollectiveOffersActionsBarProps<
    CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  >,
  features: string[] = []
) => {
  renderWithProviders(
    <>
      <CollectiveOffersActionsBar {...props} />
      <Notification />
    </>,
    {
      storeOverrides: {},
      initialRouterEntries: ['/offres/collectives'],
      features,
    }
  )
}

vi.mock('@/apiClient/api', () => ({
  api: {
    patchCollectiveOffersActiveStatus: vi.fn(),
    patchCollectiveOffersTemplateActiveStatus: vi.fn(),
    patchCollectiveOffersTemplateArchive: vi.fn(),
    patchCollectiveOffersArchive: vi.fn(),
  },
}))

const mockMutate = vi.fn()

vi.mock('swr', async () => ({
  ...(await vi.importActual('swr')),
  useSWRConfig: () => ({
    mutate: mockMutate,
  }),
}))

const mockLogEvent = vi.fn()

describe('ActionsBar', () => {
  let props: CollectiveOffersActionsBarProps<
    CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  >
  const offerIds = [1, 2]
  let stocks: Array<CollectiveOffersStockResponseModel>

  beforeEach(() => {
    stocks = [
      {
        startDatetime: String(new Date()),
        hasBookingLimitDatetimePassed: true,
        remainingQuantity: 1,
      },
    ]
    props = {
      selectedOffers: offerIds.map((offerId) => ({
        ...collectiveOfferFactory({ hasBookingLimitDatetimesPassed: false }),
        id: offerId,
      })),
      clearSelectedOfferIds: vi.fn(),
      areTemplateOffers: false,
      areAllOffersSelected: false,
    }
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(api, 'patchCollectiveOffersArchive').mockResolvedValue()
  })

  it('should have publish, hide, archive, cancel CTAs offers are template', () => {
    renderActionsBar({ ...props, areTemplateOffers: true })

    expect(
      screen.getByText('Publier', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.getByText('Mettre en pause', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.getByText('Archiver', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.getByText('Annuler', { selector: 'button' })
    ).toBeInTheDocument()
  })

  it('should have archive and cancel CTAs when and offers are bookable', () => {
    renderActionsBar({ ...props, areTemplateOffers: false })

    expect(
      screen.queryByText('Publier', { selector: 'button' })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Mettre en pause', { selector: 'button' })
    ).not.toBeInTheDocument()
    expect(
      screen.getByText('Archiver', { selector: 'button' })
    ).toBeInTheDocument()
    expect(
      screen.getByText('Annuler', { selector: 'button' })
    ).toBeInTheDocument()
  })

  it('should say how many offers are selected when only 1 offer is selected', () => {
    props.selectedOffers = [collectiveOfferFactory()]

    renderActionsBar(props)

    expect(screen.getByText('1 offre sélectionnée')).toBeInTheDocument()
  })

  it('should say how many offers are selected when more than 1 offer are selected', () => {
    renderActionsBar(props)

    expect(screen.getByText('2 offres sélectionnées')).toBeInTheDocument()
  })

  it('should show a generic count when more than 500 offers are selected', () => {
    props.selectedOffers = Array(501)
      .fill(null)
      .map((_val, i) => ({ ...collectiveOfferFactory(), id: i }))

    renderActionsBar(props)

    expect(screen.getByText('100+ offres sélectionnées')).toBeInTheDocument()
  })

  it('should hide selected offers when CAN_HIDE action is allowed and offers are template', async () => {
    renderActionsBar({
      ...props,
      areAllOffersSelected: false,
      areTemplateOffers: true,
      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
          isShowcase: true,
        }),
        collectiveOfferFactory({
          id: 2,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
          isShowcase: true,
        }),
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
        from: '/offres/collectives',
        has_selected_all_offers: false,
      }
    )
    expect(
      api.patchCollectiveOffersTemplateActiveStatus
    ).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: false,
    })
    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)

    expect(
      screen.getByText('2 offres ont bien été mises en pause')
    ).toBeInTheDocument()
  })

  it('should unselect offers and hide action bar on click on "Annuler" button', async () => {
    renderActionsBar(props)

    await userEvent.click(screen.getByText('Annuler'))

    expect(props.clearSelectedOfferIds).toHaveBeenCalledTimes(1)
  })

  it('should show an error message when an error occurs after clicking on "Archiver" button when some offers are selected', async () => {
    vi.spyOn(api, 'patchCollectiveOffersArchive').mockRejectedValueOnce(null)
    renderActionsBar({
      ...props,
      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        }),
      ],
    })

    const archiveButton = screen.getByText('Archiver')
    await userEvent.click(archiveButton)

    const modalArchiveButton = screen.getByText('Archiver l’offre')
    await userEvent.click(modalArchiveButton)

    expect(
      screen.getByText('Une erreur est survenue lors de l’archivage de l’offre')
    )
  })

  it('should only make one call if the ids all come from template offer', async () => {
    renderActionsBar({
      ...props,
      areAllOffersSelected: false,
      areTemplateOffers: true,
      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          isShowcase: true,
        }),
        collectiveOfferFactory({
          id: 2,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          isShowcase: true,
        }),
      ],
    })

    await userEvent.click(screen.getByText('Mettre en pause'))
    const confirmDeactivateButton = screen.getAllByText('Mettre en pause')[1]
    await userEvent.click(confirmDeactivateButton)

    expect(
      api.patchCollectiveOffersTemplateActiveStatus
    ).toHaveBeenLastCalledWith({
      ids: [1, 2],
      isActive: false,
    })
  })

  it('should call tracker event when archiving an offer', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
          stocks,
        }),
        collectiveOfferFactory({
          id: 2,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
          stocks,
          isShowcase: true,
        }),
      ],
    })

    const archivingButton = screen.getByText('Archiver')
    await userEvent.click(archivingButton)

    const confirmArchivingButton = screen.getByText('Archiver les offres')
    await userEvent.click(confirmArchivingButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_ARCHIVE_COLLECTIVE_OFFER,
      {
        from: '/offres/collectives',
        offerType: 'collective',
        selected_offers: JSON.stringify([
          {
            offerId: '1',
            offerStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          },
          {
            offerId: '2',
            offerStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          },
        ]),
      }
    )
  })

  it('should archive offers on click on "Archiver" when CAN_ARCHIVE is allowed', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          stocks,
          allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        }),
        collectiveOfferFactory({
          id: 2,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          stocks,
          allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        }),
      ],
    })

    const archivingButton = screen.getByText('Archiver')
    await userEvent.click(archivingButton)

    const confirmArchivingButton = screen.getByText('Archiver les offres')
    await userEvent.click(confirmArchivingButton)

    expect(api.patchCollectiveOffersArchive).toHaveBeenLastCalledWith({
      ids: [1, 2],
    })

    expect(
      screen.getByText('2 offres ont bien été archivées')
    ).toBeInTheDocument()
  })

  it('should not archive offers on click on "Archiver" when at least one offer cannot be archived', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        collectiveOfferFactory({
          id: 1,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          stocks,
          allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        }),
        collectiveOfferFactory({
          id: 2,
          displayedStatus: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
          stocks,
          allowedActions: [],
        }),
      ],
    })

    const archivingButton = screen.getByText('Archiver')
    await userEvent.click(archivingButton)

    expect(
      screen.getByText(
        'Les offres déjà archivées ou liées à des réservations ne peuvent pas être archivées'
      )
    ).toBeInTheDocument()
  })

  it('should refresh the bookable offers list when the offer status is modified', async () => {
    renderActionsBar({
      ...props,
      selectedOffers: [
        collectiveOfferFactory({
          isShowcase: false,
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          hasBookingLimitDatetimesPassed: false,
          allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        }),
      ],
    })

    await userEvent.click(screen.getByText('Archiver'))
    const confirmArchivingButton = screen.getByText('Archiver l’offre')
    await userEvent.click(confirmArchivingButton)

    expect(mockMutate).toHaveBeenCalledWith(
      expect.arrayContaining(['getCollectiveOffersBookable'])
    )
  })

  it('should refresh the template offers list when the offer status is modified', async () => {
    renderActionsBar({
      ...props,
      areTemplateOffers: true,
      selectedOffers: [
        collectiveOfferFactory({
          isShowcase: true,
          displayedStatus: CollectiveOfferDisplayedStatus.HIDDEN,
          hasBookingLimitDatetimesPassed: false,
          allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
        }),
      ],
    })

    await userEvent.click(screen.getByText('Publier'))

    expect(mockMutate).toHaveBeenCalledWith(
      expect.arrayContaining(['getCollectiveOffersTemplate'])
    )
  })

  it('should publish offer when action is allowed ', async () => {
    renderActionsBar({
      ...props,
      areTemplateOffers: true,
      selectedOffers: [
        collectiveOfferFactory({
          isShowcase: true,
          displayedStatus: CollectiveOfferDisplayedStatus.HIDDEN,
          hasBookingLimitDatetimesPassed: false,
          allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
        }),
      ],
    })

    await userEvent.click(screen.getByText('Publier'))

    expect(api.patchCollectiveOffersTemplateActiveStatus).toHaveBeenCalledTimes(
      1
    )

    expect(screen.getByText('1 offre a bien été publiée')).toBeInTheDocument()
  })

  it('should display error message when trying to publish offer and CAN_PUBLISH action is not allowed', async () => {
    renderActionsBar({
      ...props,
      areTemplateOffers: true,
      selectedOffers: [
        collectiveOfferFactory({
          isShowcase: false,
          displayedStatus: CollectiveOfferDisplayedStatus.HIDDEN,
          hasBookingLimitDatetimesPassed: false,
          allowedActions: [],
        }),
      ],
    })

    await userEvent.click(screen.getByText('Publier'))

    expect(
      screen.getByText(
        'Seules les offres vitrines au statut en pause peuvent être publiées.'
      )
    ).toBeInTheDocument()
  })
})
