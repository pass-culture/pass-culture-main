import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router'

import type { ApiRequestOptions } from '@/apiClient/adage/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/adage/core/ApiResult'
import { api } from '@/apiClient/api'
import {
  ApiError,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferStep } from '../../CollectiveOfferNavigation/CollectiveCreationOfferNavigation'
import {
  CollectiveEditionOfferNavigation,
  type CollectiveEditionOfferNavigationProps,
} from '../CollectiveEditionOfferNavigation'

const templateOffer:
  | GetCollectiveOfferTemplateResponseModel
  | GetCollectiveOfferResponseModel = getCollectiveOfferTemplateFactory({})
const offerId = 1
const props: CollectiveEditionOfferNavigationProps = {
  activeStep: CollectiveOfferStep.DETAILS,
  offerId,
  isTemplate: false,
  offer: getCollectiveOfferFactory(),
}

const mockLogEvent = vi.fn()
const snackBarError = vi.fn()
const snackBarSuccess = vi.fn()
const defaultUseLocationValue = {
  state: {},
  hash: '',
  key: '',
  pathname: '',
  search: '',
}

const renderCollectiveEditingOfferNavigation = (
  props: CollectiveEditionOfferNavigationProps,
  features?: string[]
) =>
  renderWithProviders(<CollectiveEditionOfferNavigation {...props} />, {
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory(),
    },
    features,
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

    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [makeVenueListItem({ id: 2 })],
    })

    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValue(templateOffer)
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValue(
      getCollectiveOfferFactory({ id: props.offerId })
    )

    vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [],
    })

    const notifsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...notifsImport,
      error: snackBarError,
      success: snackBarSuccess,
    }))

    vi.spyOn(router, 'useLocation').mockReturnValue(defaultUseLocationValue)
  })

  it('should log event when clicking "Dupliquer" button', async () => {
    vi.spyOn(api, 'duplicateCollectiveOffer').mockResolvedValueOnce(
      // Simuler la nouvelle offre dupliquée
      getCollectiveOfferFactory({
        id: 999,
      })
    )
    vi.spyOn(api, 'attachOfferImage').mockResolvedValueOnce({
      imageUrl: 'my url',
    })

    fetchMock.mockResponseOnce((request) => {
      // Si l'offre mockée a cette URL, l'intercepter ici.
      if (
        request.url === 'https://example.com/image.jpg' &&
        request.method === 'GET'
      ) {
        return {
          status: 200,
          // Retourner un contenu simulé (ex: un faux buffer)
          body: 'Mock Image Data',
          headers: { 'Content-Type': 'image/jpeg' },
        }
      }
      return { status: 404 }
    })

    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_DUPLICATE],
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
        ...templateOffer,
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
        ...templateOffer,
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
      isTemplate: true,
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_DUPLICATE],
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
        ...templateOffer,
        allowedActions: [
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        ],
      },
    })

    const duplicateOfferButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    await userEvent.click(duplicateOfferButton)

    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  })

  it('should show an error notification when the duplication failed', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce(
      getCollectiveOfferTemplateFactory()
    )
    vi.spyOn(api, 'createCollectiveOffer').mockRejectedValueOnce(
      new ApiError({} as ApiRequestOptions, { status: 400 } as ApiResult, '')
    )

    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...templateOffer,
        allowedActions: [
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        ],
      },
    })

    const duplicateOfferButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    await userEvent.click(duplicateOfferButton)

    expect(snackBarError).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
  })

  it('should return an error when trying to get offerer image', async () => {
    // eslint-disable-next-line no-undef
    fetchMock.mockResponse('Service Unavailable', { status: 503 })

    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...templateOffer,
        allowedActions: [
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
        ],
      },
    })

    const duplicateOfferButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })

    await userEvent.click(duplicateOfferButton)

    expect(snackBarError).toHaveBeenCalledWith(
      'Impossible de dupliquer l’image'
    )
  })

  it('should show a success notification when archiving a template offer succeeds', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...templateOffer,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
      },
    })

    const archiveButton = screen.getByRole('button', {
      name: 'Archiver',
    })

    await userEvent.click(archiveButton)
    const confirmArchivingButton = screen.getByText('Archiver l’offre')
    await userEvent.click(confirmArchivingButton)

    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Une offre a bien été archivée'
    )
  })

  it('should not see archive button archive action is not possible', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...templateOffer,
        allowedActions: [],
      },
    })

    const archiveButton = screen.queryByRole('button', {
      name: 'Archiver',
    })

    expect(archiveButton).not.toBeInTheDocument()
  })

  it('should return an error on offer archiving when the offer id is not valid', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      offerId: undefined,
      isTemplate: true,
      offer: {
        ...templateOffer,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
      },
    })

    const archiveButton = screen.getByRole('button', {
      name: 'Archiver',
    })

    await userEvent.click(archiveButton)
    const confirmArchivingButton = screen.getByText('Archiver l’offre')
    await userEvent.click(confirmArchivingButton)

    expect(snackBarError).toHaveBeenNthCalledWith(
      1,
      'L’identifiant de l’offre n’est pas valide.'
    )
  })

  it('should show an error notification when archive api call fails', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: {
        ...templateOffer,
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

    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de l’archivage de l’offre'
    )
  })

  it('should not show action buttons when offer is bookable', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: false,
      offer: getCollectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_ARCHIVE,
          CollectiveOfferAllowedAction.CAN_DUPLICATE,
        ],
      }),
    })

    const archiveButton = screen.queryByRole('button', {
      name: 'Archiver',
    })
    const duplicateOfferButton = screen.queryByRole('button', {
      name: 'Dupliquer',
    })

    expect(archiveButton).not.toBeInTheDocument()
    expect(duplicateOfferButton).not.toBeInTheDocument()
  })

  it('should not show preview button when offer is template and status is archived', () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: getCollectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.ARCHIVED,
      }),
    })

    const previewButton = screen.queryByRole('button', {
      name: 'Aperçu dans ADAGE',
    })

    expect(previewButton).not.toBeInTheDocument()
  })

  it('should render share link drawer when pressing the share button', async () => {
    renderCollectiveEditingOfferNavigation({
      ...props,
      isTemplate: true,
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_SHARE],
      }),
    })

    const shareLinkButton = screen.getByRole('button', {
      name: 'Partager l’offreNouveau',
    })

    expect(shareLinkButton).toBeInTheDocument()

    await userEvent.click(shareLinkButton)
    const drawerContent = await screen.findByText(
      'Aidez les enseignants à retrouver votre offre plus facilement sur ADAGE'
    )
    expect(drawerContent).toBeInTheDocument()
  })
})
