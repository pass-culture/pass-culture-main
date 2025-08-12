import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import { ApiRequestOptions } from '@/apiClient/adage/core/ApiRequestOptions'
import { ApiResult } from '@/apiClient/adage/core/ApiResult'
import { api } from '@/apiClient/api'
import {
  ApiError,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseIdModel,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import * as useNotification from '@/commons/hooks/useNotification'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { venueListItemFactory } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { CollectiveOfferStep } from '../../CollectiveOfferNavigation/CollectiveCreationOfferNavigation'
import {
  CollectiveEditionOfferNavigation,
  CollectiveEditionOfferNavigationProps,
} from '../CollectiveEditionOfferNavigation'

const offer:
  | GetCollectiveOfferTemplateResponseModel
  | GetCollectiveOfferResponseModel = getCollectiveOfferTemplateFactory({
  isTemplate: true,
})
const offerId = 1
const props: CollectiveEditionOfferNavigationProps = {
  activeStep: CollectiveOfferStep.DETAILS,
  offerId,
  isTemplate: false,
  offer: getCollectiveOfferFactory(),
}

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

const renderCollectiveEditingOfferNavigation = (
  props: CollectiveEditionOfferNavigationProps,
  options?: RenderWithProvidersOptions
) =>
  renderWithProviders(<CollectiveEditionOfferNavigation {...props} />, {
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory(),
    },
    ...options,
  })

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useLocation: vi.fn(),
}))

describe('CollectiveEditionOfferNavigation', () => {
  beforeEach(async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValue(offer)

    vi.spyOn(api, 'getVenue').mockResolvedValue(defaultGetVenue)
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [venueListItemFactory()],
    })

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
  })

  it('should log event when clicking "Dupliquer" button', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_DUPLICATE],
      }),
    })

    const duplicateOffer = screen.getByRole('button', {
      name: 'Dupliquer',
    })
    await userEvent.click(duplicateOffer)

    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DUPLICATE_BOOKABLE_OFFER,
      {
        from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_RECAP,
        offererId: '1',
        offerId: 1,
        offerType: 'collective',
        offerStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      }
    )
  })

  it('should show create bookable offer when CAN_CREATE_BOOKABLE_OFFER is allowed', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...offer,
        allowedActions: [
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        ],
      },
    })

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    expect(duplicateOffer).toBeInTheDocument()
  })

  it('should not show create bookable offer when CAN_CREATE_BOOKABLE_OFFER is not allowed', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...offer,
        allowedActions: [],
      },
    })

    const duplicateOfferButton = screen.queryByRole('button', {
      name: 'Créer une offre réservable',
    })

    expect(duplicateOfferButton).not.toBeInTheDocument()
  })

  it('should show duplicate button when CAN_DUPLICATE is allowed', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: false,
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_DUPLICATE],
      }),
    })

    const duplicateOffer = screen.getByRole('button', {
      name: 'Dupliquer',
    })

    expect(duplicateOffer).toBeInTheDocument()
  })

  it('should not show duplicate button when CAN_DUPLICATE is not allowed', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: false,
      offer: getCollectiveOfferFactory({
        allowedActions: [],
      }),
    })

    const duplicateOfferButton = screen.queryByRole('button', {
      name: 'Dupliquer',
    })

    expect(duplicateOfferButton).not.toBeInTheDocument()
  })

  it('should return an error when the collective offer could not be retrieved', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValueOnce('error')

    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...offer,
        allowedActions: [
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        ],
      },
    })

    const duplicateOfferButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    await userEvent.click(duplicateOfferButton)

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  })

  it('should show an error notification when the duplication failed', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce(
      getCollectiveOfferTemplateFactory({ isTemplate: true, isActive: true })
    )
    vi.spyOn(api, 'createCollectiveOffer').mockRejectedValueOnce(
      new ApiError({} as ApiRequestOptions, { status: 400 } as ApiResult, '')
    )

    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...offer,
        allowedActions: [
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        ],
      },
    })

    const duplicateOfferButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    await userEvent.click(duplicateOfferButton)

    expect(notifyError).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
  })

  it('should return an error when trying to get offerer image', async () => {
    // eslint-disable-next-line no-undef
    fetchMock.mockResponse('Service Unavailable', { status: 503 })

    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...offer,
        allowedActions: [
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        ],
      },
    })

    const duplicateOfferButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    await userEvent.click(duplicateOfferButton)

    expect(notifyError).toHaveBeenCalledWith('Impossible de dupliquer l’image')
  })

  it('should show a success notification when archiving a template offer succeeds', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...offer,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
      },
    })

    const archiveButton = screen.getByRole('button', {
      name: 'Archiver',
    })

    await userEvent.click(archiveButton)
    const confirmArchivingButton = screen.getByText('Archiver l’offre')
    await userEvent.click(confirmArchivingButton)

    expect(notifySuccess).toHaveBeenCalledWith(
      'Une offre a bien été archivée',
      {
        duration: 8000,
      }
    )
  })

  it('should show a success notification when archiving a bookable offer succeeds', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: false,
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
      }),
    })

    const archiveButton = screen.getByRole('button', {
      name: 'Archiver',
    })

    await userEvent.click(archiveButton)
    const confirmArchivingButton = screen.getByText('Archiver l’offre')
    await userEvent.click(confirmArchivingButton)

    expect(notifySuccess).toHaveBeenCalledWith(
      'Une offre a bien été archivée',
      {
        duration: 8000,
      }
    )
  })

  it('should not see archive button archive action is not possible', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...offer,
        allowedActions: [],
      },
    })

    const archiveButton = screen.queryByRole('button', {
      name: 'Archiver',
    })

    expect(archiveButton).not.to.toBeInTheDocument()
  })

  it('should return an error on offer archiving when the offer id is not valid', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      offerId: undefined,
      isTemplate: true,
      offer: {
        ...offer,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
      },
    })

    const archiveButton = screen.getByRole('button', {
      name: 'Archiver',
    })

    await userEvent.click(archiveButton)
    const confirmArchivingButton = screen.getByText('Archiver l’offre')
    await userEvent.click(confirmArchivingButton)

    expect(notifyError).toHaveBeenNthCalledWith(
      1,
      'L’identifiant de l’offre n’est pas valide.'
    )
  })

  it('should show an error notification when archive api call fails', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...offer,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
      },
    })

    vi.spyOn(api, 'patchCollectiveOffersTemplateArchive').mockRejectedValueOnce(
      {}
    )

    const archiveButton = screen.getByRole('button', {
      name: 'Archiver',
    })

    await userEvent.click(archiveButton)
    const confirmArchivingButton = screen.getByText('Archiver l’offre')
    await userEvent.click(confirmArchivingButton)

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de l’archivage de l’offre',
      {
        duration: 8000,
      }
    )
  })
})
