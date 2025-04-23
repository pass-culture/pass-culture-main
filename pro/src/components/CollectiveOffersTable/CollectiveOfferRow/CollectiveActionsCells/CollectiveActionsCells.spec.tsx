import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { beforeEach, expect } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { api } from 'apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
  OfferAddressType,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from 'commons/core/FirebaseEvents/constants'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from 'commons/core/Offers/constants'
import * as useNotification from 'commons/hooks/useNotification'
import {
  collectiveOfferFactory,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
  getCollectiveOfferVenueFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import { venueListItemFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import * as storageAvailable from 'commons/utils/storageAvailable'

import {
  CollectiveActionsCells,
  CollectiveActionsCellsProps,
} from './CollectiveActionsCells'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  return {
    ...(await vi.importActual('react-router-dom')),
    useNavigate: () => mockNavigate,
    default: vi.fn(),
  }
})

const mockLogEvent = vi.fn()

const mockDeselectOffer = vi.fn()
const renderCollectiveActionsCell = (
  props: Partial<CollectiveActionsCellsProps> = {},
  features: string[] = []
) => {
  const defaultProps: CollectiveActionsCellsProps = {
    offer: collectiveOfferFactory(),
    editionOfferLink: '',
    urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    isSelected: false,
    deselectOffer: mockDeselectOffer,
    rowId: 'rowId',
    ...props,
  }

  return renderWithProviders(
    <table>
      <tbody>
        <tr>
          <CollectiveActionsCells {...defaultProps} />
        </tr>
      </tbody>
    </table>,
    { features }
  )
}

vi.mock('apiClient/api', () => ({
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

describe('CollectiveActionsCells', () => {
  const notifyError = vi.fn()
  const notifySuccess = vi.fn()

  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
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
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        stocks: [
          {
            startDatetime: String(new Date()),
            hasBookingLimitDatetimePassed: true,
            remainingQuantity: 1,
          },
        ],
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

  it('should deselect an offer selected when the offer has just been archived', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        stocks: [
          {
            startDatetime: String(new Date()),
            hasBookingLimitDatetimePassed: true,
            remainingQuantity: 1,
          },
        ],
      }),
      isSelected: true,
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

    expect(mockDeselectOffer).toHaveBeenCalledTimes(1)
  })

  it('should show action buttons when action is allowed on bookable offer', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: false,
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
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
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
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: false,
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
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
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
        venues: [venueListItemFactory({ id: 4 })],
      })
    })

    it('should show an error when bookable offer duplication fails', async () => {
      vi.spyOn(api, 'getCollectiveOffer').mockRejectedValueOnce({})
      renderCollectiveActionsCell({
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
      renderCollectiveActionsCell({
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

      renderCollectiveActionsCell({
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
        }
      )
    })

    it('should enable bookable offer creation from template', async () => {
      Storage.prototype.getItem = vi.fn(() => 'true')

      const collectiveOfferTemplate = getCollectiveOfferTemplateFactory({
        imageUrl: 'https://http.cat/201',
        imageCredit: 'chats',
        venue: getCollectiveOfferVenueFactory({ id: 4 }),
      })
      vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce(
        collectiveOfferTemplate
      )
      vi.spyOn(api, 'createCollectiveOffer').mockResolvedValueOnce({ id: 202 })
      renderCollectiveActionsCell({
        offer: collectiveOfferFactory({
          id: 200,
          isShowcase: true,
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
        interventionArea: ['mainland'],
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: false,
        name: 'Offre de test',
        nationalProgramId: 1,
        offerVenue: {
          addressType: OfferAddressType.OTHER,
          otherAddress: 'A la mairie',
          venueId: 0,
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
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
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
  ])(
    'should show edition button when the $name edition action is allowed',
    async ({ actions }) => {
      renderCollectiveActionsCell({
        offer: collectiveOfferFactory({
          isShowcase: false,
          allowedActions: actions,
        }),
      })

      await userEvent.click(
        screen.getByRole('button', { name: 'Voir les actions' })
      )

      expect(screen.getByText('Modifier')).toBeInTheDocument()
    }
  )

  it('should not show edition button when no edition action is allowed', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: false,
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
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
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
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_PUBLISH],
        isActive: false,
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
})
