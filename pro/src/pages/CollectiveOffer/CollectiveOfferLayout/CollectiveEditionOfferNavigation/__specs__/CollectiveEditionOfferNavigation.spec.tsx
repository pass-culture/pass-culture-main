import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import { ApiRequestOptions } from 'apiClient/adage/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/adage/core/ApiResult'
import { api } from 'apiClient/api'
import {
  ApiError,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseIdModel,
  CollectiveOfferStatus,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from 'commons/core/FirebaseEvents/constants'
import { SENT_DATA_ERROR_MESSAGE } from 'commons/core/shared/constants'
import * as useNotification from 'commons/hooks/useNotification'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import {
  sharedCurrentUserFactory,
  currentOffererFactory,
} from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { CollectiveOfferStep } from '../../CollectiveOfferNavigation/CollectiveCreationOfferNavigation'
import {
  CollectiveEditionOfferNavigation,
  CollectiveEditionOfferNavigationProps,
} from '../CollectiveEditionOfferNavigation'

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
  let offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
  let props: CollectiveEditionOfferNavigationProps
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
      status: CollectiveOfferStatus.ACTIVE,
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
    vi.spyOn(api, 'getNationalPrograms').mockResolvedValue([])

    vi.spyOn(api, 'createCollectiveOffer').mockResolvedValue(
      {} as CollectiveOfferResponseIdModel
    )

    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
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

  it('should log event when clicking "Dupliquer" button', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
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
        offerStatus: CollectiveOfferDisplayedStatus.ACTIVE,
      }
    )
  })

  it('should show create bookable offer if offer is template in edition', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
    })

    const duplicateOfferButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    expect(duplicateOfferButton).toBeInTheDocument()
  })

  it('should show create bookable offer if offer is template and ff is active', () => {
    renderCollectiveEditingOfferNavigation(
      {
        ...props,
        isTemplate: true,
        offer: {
          ...offer,
          allowedActions: [
            CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
          ],
        },
      },
      { features: ['ENABLE_COLLECTIVE_NEW_STATUSES'] }
    )

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    expect(duplicateOffer).toBeInTheDocument()
  })

  it('should show duplicate button if offer is bookable and ff is active', () => {
    renderCollectiveEditingOfferNavigation(
      {
        ...props,
        isTemplate: false,
        offer: getCollectiveOfferFactory({
          allowedActions: [CollectiveOfferAllowedAction.CAN_DUPLICATE],
        }),
      },
      { features: ['ENABLE_COLLECTIVE_NEW_STATUSES'] }
    )

    const duplicateOffer = screen.getByRole('button', {
      name: 'Dupliquer',
    })

    expect(duplicateOffer).toBeInTheDocument()
  })

  it('should return an error when the collective offer could not be retrieved', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValueOnce('')

    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
    })

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  })

  it('should return an error when the duplication failed', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce(
      getCollectiveOfferTemplateFactory({ isTemplate: true, isActive: true })
    )
    vi.spyOn(api, 'createCollectiveOffer').mockRejectedValueOnce(
      new ApiError({} as ApiRequestOptions, { status: 400 } as ApiResult, '')
    )

    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
    })

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
  })

  it('should return an error when trying to get offerer image', async () => {
    // eslint-disable-next-line no-undef
    fetchMock.mockResponse('Service Unavailable', { status: 503 })

    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
    })

    const duplicateOffer = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    await userEvent.click(duplicateOffer)

    expect(notifyError).toHaveBeenCalledWith('Impossible de dupliquer l’image')
  })

  it('should archive an offer template', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer,
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

  it('should archive an offer bookable', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: false,
      offer,
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

  it('should not see archive button when offer is not archivable', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: { ...offer, status: CollectiveOfferStatus.ARCHIVED },
    })

    const archiveButton = screen.queryByRole('button', {
      name: 'Archiver',
    })

    expect(archiveButton).not.toBeInTheDocument()
  })

  it('should not see archive button when FF status is enable and archive action is not possible', () => {
    renderCollectiveEditingOfferNavigation(
      {
        ...props,
        isTemplate: true,
        offer: {
          ...offer,
          allowedActions: [],
        },
      },
      { features: ['ENABLE_COLLECTIVE_NEW_STATUSES'] }
    )

    const archiveButton = screen.queryByRole('button', {
      name: 'Archiver',
    })

    expect(archiveButton).not.to.toBeInTheDocument()
  })

  it('should see archive button when FF status is enable and archive action is possible for template offer', () => {
    renderCollectiveEditingOfferNavigation(
      {
        ...props,
        isTemplate: true,
        offer: {
          ...offer,
          allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
        },
      },
      { features: ['ENABLE_COLLECTIVE_NEW_STATUSES'] }
    )

    const archiveButton = screen.getByRole('button', {
      name: 'Archiver',
    })

    expect(archiveButton).toBeInTheDocument()
  })

  it('should see archive button when FF status is enable and archive action is possible for bookable offer', () => {
    renderCollectiveEditingOfferNavigation(
      {
        ...props,
        isTemplate: false,
        offer: getCollectiveOfferFactory({
          allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        }),
      },
      { features: ['ENABLE_COLLECTIVE_NEW_STATUSES'] }
    )

    const archiveButton = screen.getByRole('button', {
      name: 'Archiver',
    })

    expect(archiveButton).toBeInTheDocument()
  })

  it('should return an error on offer archiving when the offer id is not valid', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      offerId: undefined,
      isTemplate: true,
      offer,
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

  it('should return an error on offer archiving when there is an api error', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer,
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

  it('should not display the edition button for archived collective offers', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      offerId: 1,
      isTemplate: false,
      offer: getCollectiveOfferFactory({
        status: CollectiveOfferStatus.ARCHIVED,
      }),
    })

    expect(
      screen.queryByRole('link', { name: 'Modifier l’offre' })
    ).not.toBeInTheDocument()
  })

  it('should not display the navigation for archived collective offers', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      offerId: 1,
      isTemplate: false,
      offer: getCollectiveOfferFactory({
        status: CollectiveOfferStatus.ARCHIVED,
      }),
    })

    expect(screen.queryByTestId('stepper')).not.toBeInTheDocument()
  })
})
