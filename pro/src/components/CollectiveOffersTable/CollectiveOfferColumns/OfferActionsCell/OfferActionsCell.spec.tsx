import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { beforeEach, expect } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { api } from '@/apiClient/api'
import {
  CollectiveLocationType,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import * as useNotification from '@/commons/hooks/useNotification'
import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
  getCollectiveOfferVenueFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { getLocationResponseModel } from '@/commons/utils/factories/commonOffersApiFactories'
import {
  defaultGetOffererResponseModel,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import * as storageAvailable from '@/commons/utils/storageAvailable'

import {
  OfferActionsCell,
  type OfferActionsCellProps,
} from './OfferActionsCell'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const mockNavigate = vi.fn()
vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
    default: vi.fn(),
  }
})

const mockLogEvent = vi.fn()

const renderOfferActionsCell = (
  props: Partial<OfferActionsCellProps> = {},
  features: string[] = []
) => {
  const defaultProps: OfferActionsCellProps = {
    offer: collectiveOfferFactory(),
    urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    ...props,
  }

  return renderWithProviders(<OfferActionsCell {...defaultProps} />, {
    features,
    storeOverrides: {
      offerer: {
        currentOfferer: { ...defaultGetOffererResponseModel, id: 1 },
      },
    },
  })
}

vi.mock('@/apiClient/api', () => ({
  api: {
    patchCollectiveOffersArchive: vi.fn(),
    createCollectiveOffer: vi.fn(),
    getCollectiveOffer: vi.fn(),
    listEducationalOfferers: vi.fn(),
    duplicateCollectiveOffer: vi.fn(),
    attachOfferImage: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    patchCollectiveOffersTemplateActiveStatus: vi.fn(),
    getVenues: vi.fn(),
  },
}))
vi.spyOn(storageAvailable, 'storageAvailable').mockImplementationOnce(
  () => true
)

describe('OfferActionsCells', () => {
  const notifyError = vi.fn()
  const notifySuccess = vi.fn()

  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      '@/commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      success: notifySuccess,
      error: notifyError,
    }))
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should archive an offer on click on the action', async () => {
    renderOfferActionsCell({
      offer: collectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        dates: {
          start: String(new Date()),
          end: String(new Date()),
        },
        stock: {
          numberOfTickets: 1,
        },
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    const archiveOfferButton = screen.getByText('Archiver')
    await userEvent.click(archiveOfferButton)

    const modalTitle = screen.getByText(
      'Êtes-vous sûr de vouloir archiver cette offre ?'
    )
    expect(modalTitle).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Archiver l’offre' })
    )

    expect(api.patchCollectiveOffersArchive).toHaveBeenCalledTimes(1)
  })

  it('should show action buttons when action is allowed on bookable offer', async () => {
    renderOfferActionsCell({
      offer: collectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_ARCHIVE,
          CollectiveOfferAllowedAction.CAN_DUPLICATE,
          CollectiveOfferAllowedAction.CAN_EDIT_DATES,
          CollectiveOfferAllowedAction.CAN_CANCEL,
        ],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    expect(screen.getByText('Archiver')).toBeInTheDocument()
    expect(screen.getByText('Dupliquer')).toBeInTheDocument()
    expect(screen.getByText('Modifier')).toBeInTheDocument()
    expect(screen.getByText('Annuler la réservation')).toBeInTheDocument()
  })

  it('should show action buttons when action is allowed on template offer', async () => {
    renderOfferActionsCell({
      offer: collectiveOfferTemplateFactory({
        allowedActions: [
          CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE,
          CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
          CollectiveOfferTemplateAllowedAction.CAN_DUPLICATE,
          CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
          CollectiveOfferTemplateAllowedAction.CAN_HIDE,
          CollectiveOfferTemplateAllowedAction.CAN_PUBLISH,
        ],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    expect(screen.getByText('Archiver')).toBeInTheDocument()
    expect(screen.getByText('Créer une offre réservable')).toBeInTheDocument()
    expect(screen.getByText('Modifier')).toBeInTheDocument()
    expect(screen.getByText('Mettre en pause')).toBeInTheDocument()
    expect(screen.getByText('Publier')).toBeInTheDocument()
  })

  it('should not show action buttons when action is not allowed', async () => {
    renderOfferActionsCell({
      offer: collectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_ARCHIVE, // keep one action to click on "Voir les actions"
        ],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    expect(screen.getByText('Archiver')).toBeInTheDocument()
    expect(screen.queryByText('Dupliquer')).not.toBeInTheDocument()
    expect(screen.queryByText('Modifier')).not.toBeInTheDocument()
    expect(screen.queryByText('Annuler la réservation')).not.toBeInTheDocument()
  })

  it('should not show "Voir les actions" button when no action is allowed', () => {
    renderOfferActionsCell({
      offer: collectiveOfferTemplateFactory({
        allowedActions: [],
      }),
    })

    expect(
      screen.queryByRole('button', { name: 'Voir les actions' })
    ).not.toBeInTheDocument()
  })

  describe('CollectiveActionsCells:Duplicate', () => {
    beforeEach(() => {
      vi.spyOn(api, 'listEducationalOfferers').mockResolvedValueOnce({
        educationalOfferers: [],
      })
      vi.spyOn(api, 'getVenues').mockResolvedValue({
        venues: [makeVenueListItem({ id: 4 })],
      })
    })

    it('should show an error when bookable offer duplication fails', async () => {
      vi.spyOn(api, 'getCollectiveOffer').mockRejectedValueOnce({})
      renderOfferActionsCell({
        offer: collectiveOfferFactory({
          id: 200,
          allowedActions: [CollectiveOfferAllowedAction.CAN_DUPLICATE],
        }),
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Voir les actions' })
      )
      await userEvent.click(screen.getByText('Dupliquer'))
      expect(notifyError).toBeCalledWith(
        'Une erreur est survenue lors de la récupération de votre offre'
      )
    })

    it('should duplicate a bookable', async () => {
      vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
        getCollectiveOfferFactory({
          imageUrl: 'https://http.cat/201',
          imageCredit: 'chats',
        })
      )

      vi.spyOn(api, 'duplicateCollectiveOffer').mockResolvedValueOnce(
        getCollectiveOfferFactory({ id: 201 })
      )
      renderOfferActionsCell({
        offer: collectiveOfferFactory({
          id: 200,
          allowedActions: [CollectiveOfferAllowedAction.CAN_DUPLICATE],
        }),
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Voir les actions' })
      )
      await userEvent.click(screen.getByText('Dupliquer'))
      expect(api.duplicateCollectiveOffer).toBeCalledWith(200)
      expect(fetchMock).toHaveBeenCalledWith('https://http.cat/201')
      expect(api.attachOfferImage).toBeCalledWith(201, {
        credit: 'chats',
        croppingRectHeight: 1,
        croppingRectWidth: 1,
        croppingRectX: 0,
        croppingRectY: 0,
        thumb: expect.anything(),
      })
      expect(mockNavigate).toHaveBeenCalledWith(
        '/offre/collectif/201/creation?structure=1'
      )
    })

    it('should log event when duplicating a bookable offer', async () => {
      vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
        getCollectiveOfferFactory({
          imageUrl: 'https://http.cat/201',
          imageCredit: 'chats',
        })
      )

      renderOfferActionsCell({
        offer: collectiveOfferFactory({
          id: 200,
          allowedActions: [CollectiveOfferAllowedAction.CAN_DUPLICATE],
        }),
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Voir les actions' })
      )
      await userEvent.click(screen.getByText('Dupliquer'))
      expect(mockLogEvent).toHaveBeenCalledTimes(1)
      expect(mockLogEvent).toHaveBeenNthCalledWith(
        1,
        Events.CLICKED_DUPLICATE_BOOKABLE_OFFER,
        {
          from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFERS,
          offerId: 200,
          offerStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          offerType: 'collective',
          offererId: '1',
        }
      )
    })

    it('should enable bookable offer creation from template', async () => {
      Storage.prototype.getItem = vi.fn(() => 'true')

      const collectiveOfferTemplate = getCollectiveOfferTemplateFactory({
        imageUrl: 'https://http.cat/201',
        imageCredit: 'chats',
        venue: getCollectiveOfferVenueFactory({ id: 4 }),
        location: {
          locationType: CollectiveLocationType.ADDRESS,
          location: getLocationResponseModel({
            isVenueLocation: true,
            isManualEdition: false,
            label: 'Structure 4',
          }),
        },
      })
      vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce(
        collectiveOfferTemplate
      )
      vi.spyOn(api, 'createCollectiveOffer').mockResolvedValueOnce({ id: 202 })
      renderOfferActionsCell({
        offer: collectiveOfferTemplateFactory({
          id: 200,
          allowedActions: [
            CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
          ],
        }),
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Voir les actions' })
      )
      await userEvent.click(screen.getByText('Créer une offre réservable'))
      expect(api.createCollectiveOffer).toBeCalledWith({
        audioDisabilityCompliant: false,
        bookingEmails: ['toto@example.com'],
        contactEmail: 'toto@example.com',
        contactPhone: '0600000000',
        description: 'blablabla,',
        domains: [1],
        durationMinutes: undefined,
        formats: ['Atelier de pratique'],
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        name: 'Offre de test',
        nationalProgramId: 1,
        interventionArea: [],
        location: {
          location: {
            isVenueLocation: true,
          },
          locationType: 'ADDRESS',
        },
        students: ['Collège - 3e'],
        templateId: 200,
        venueId: 4,
        visualDisabilityCompliant: false,
      })
      expect(fetchMock).toHaveBeenCalledWith('https://http.cat/201')
      expect(api.attachOfferImage).toBeCalledWith(202, {
        credit: 'chats',
        croppingRectHeight: 1,
        croppingRectWidth: 1,
        croppingRectX: 0,
        croppingRectY: 0,
        thumb: expect.anything(),
      })
      expect(mockNavigate).toHaveBeenCalledWith(
        '/offre/collectif/202/creation?structure=4'
      )
    })
  })

  it('should not allow template offer edition for a template offer when details edition is not allowed', async () => {
    renderOfferActionsCell({
      offer: collectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    expect(screen.queryByText('Modifier')).not.toBeInTheDocument()
  })

  it.each([
    {
      actions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      name: 'details',
    },
    {
      actions: [
        CollectiveOfferAllowedAction.CAN_ARCHIVE,
        CollectiveOfferAllowedAction.CAN_EDIT_DATES,
      ],
      name: 'dates',
    },
    {
      actions: [
        CollectiveOfferAllowedAction.CAN_CANCEL,
        CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
        CollectiveOfferAllowedAction.CAN_ARCHIVE,
      ],
      name: 'discount',
    },
    {
      actions: [CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION],
      name: 'institution',
    },
  ])('should show edition button when the $name edition action is allowed', async ({
    actions,
  }) => {
    renderOfferActionsCell({
      offer: collectiveOfferFactory({
        allowedActions: actions,
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    expect(screen.getByText('Modifier')).toBeInTheDocument()
  })

  it('should not show edition button when no edition action is allowed', async () => {
    renderOfferActionsCell({
      offer: collectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_ARCHIVE,
          CollectiveOfferAllowedAction.CAN_CANCEL,
        ],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    expect(screen.queryByText('Modifier')).not.toBeInTheDocument()
  })

  it('should hide template offer on hide button press', async () => {
    renderOfferActionsCell({
      offer: collectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Mettre en pause',
      })
    )

    expect(notifySuccess).toHaveBeenCalledWith(
      'Votre offre est mise en pause et n’est plus visible sur ADAGE'
    )
  })

  it('should publish template offer on publish button press', async () => {
    renderOfferActionsCell({
      offer: collectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
        displayedStatus: CollectiveOfferDisplayedStatus.HIDDEN,
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Publier',
      })
    )

    expect(notifySuccess).toHaveBeenCalledWith(
      'Votre offre est maintenant active et visible dans ADAGE'
    )
  })

  it('should show error notification if toggling template active state fails', async () => {
    vi.spyOn(
      api,
      'patchCollectiveOffersTemplateActiveStatus'
    ).mockRejectedValueOnce(new Error('fail'))

    renderOfferActionsCell({
      offer: collectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_HIDE],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Mettre en pause' })
    )

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la désactivation de votre offre.'
    )
  })

  it('should show error notification if toggling template to active state fails', async () => {
    vi.spyOn(
      api,
      'patchCollectiveOffersTemplateActiveStatus'
    ).mockRejectedValueOnce(new Error('fail'))

    renderOfferActionsCell({
      offer: collectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Publier' }))

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de l’activation de votre offre.'
    )
  })

  it('should show error notification when archiving fails', async () => {
    vi.spyOn(api, 'patchCollectiveOffersArchive').mockRejectedValueOnce(
      new Error('fail')
    )

    renderOfferActionsCell({
      offer: collectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
      }),
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )
    await userEvent.click(screen.getByText('Archiver'))
    await userEvent.click(
      screen.getByRole('button', { name: 'Archiver l’offre' })
    )

    expect(notifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de l’archivage de l’offre',
      expect.any(Object)
    )
  })
})
