import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { beforeEach, expect } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { api } from 'apiClient/api'
import { CollectiveOfferStatus, OfferAddressType } from 'apiClient/v1'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from 'commons/core/Offers/constants'
import * as useNotification from 'commons/hooks/useNotification'
import {
  collectiveOfferFactory,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
  getCollectiveOfferVenueFactory,
} from 'commons/utils/collectiveApiFactories'
import * as localStorageAvailable from 'commons/utils/localStorageAvailable'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  CollectiveActionsCells,
  CollectiveActionsCellsProps,
} from '../CollectiveActionsCells'

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

const mockDeselectOffer = vi.fn()
const notifyError = vi.fn()
const renderCollectiveActionsCell = (
  props: Partial<CollectiveActionsCellsProps> = {}
) => {
  const defaultProps: CollectiveActionsCellsProps = {
    offer: collectiveOfferFactory(),
    editionOfferLink: '',
    urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    isSelected: false,
    deselectOffer: mockDeselectOffer,
    ...props,
  }

  return renderWithProviders(
    <table>
      <tbody>
        <tr>
          <CollectiveActionsCells {...defaultProps} />
        </tr>
      </tbody>
    </table>
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
  },
}))
vi.spyOn(localStorageAvailable, 'localStorageAvailable').mockImplementationOnce(
  () => true
)

describe('CollectiveActionsCells', () => {
  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
      success: vi.fn(),
    }))
  })

  it('should archive an offer on click on the action', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        stocks: [
          {
            beginningDatetime: String(new Date()),
            hasBookingLimitDatetimePassed: true,
            remainingQuantity: 1,
          },
        ],
      }),
    })

    await userEvent.click(screen.getByTitle('Action'))

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
        stocks: [
          {
            beginningDatetime: String(new Date()),
            hasBookingLimitDatetimePassed: true,
            remainingQuantity: 1,
          },
        ],
      }),
      isSelected: true,
    })

    await userEvent.click(screen.getByTitle('Action'))

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

  it('should not display duplicate button for draft template offer', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
        status: CollectiveOfferStatus.DRAFT,
      }),
    })

    await userEvent.click(screen.getByTitle('Action'))

    expect(
      screen.queryByText('Créer une offre réservable')
    ).not.toBeInTheDocument()
  })

  it('should not display duplicate button for draft bookable offer', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        status: CollectiveOfferStatus.DRAFT,
      }),
    })

    await userEvent.click(screen.getByTitle('Action'))

    expect(screen.queryByText('Dupliquer')).not.toBeInTheDocument()
  })

  it('should display duplicate button for template offer', async () => {
    renderCollectiveActionsCell({
      offer: collectiveOfferFactory({
        isShowcase: true,
      }),
    })

    await userEvent.click(screen.getByTitle('Action'))

    expect(screen.getByText('Créer une offre réservable')).toBeInTheDocument()
  })

  it('should display duplicate button for draft bookable offer', async () => {
    renderCollectiveActionsCell()

    await userEvent.click(screen.getByTitle('Action'))

    expect(screen.getByText('Dupliquer')).toBeInTheDocument()
  })
  describe('CollectiveActionsCells:Duplicate', () => {
    beforeEach(() => {
      vi.spyOn(api, 'listEducationalOfferers').mockResolvedValueOnce({
        educationalOfferers: [],
      })
    })

    it('should try to duplicate a bookable with collective offer error', async () => {
      vi.spyOn(api, 'getCollectiveOffer').mockRejectedValueOnce({})
      renderCollectiveActionsCell({
        offer: collectiveOfferFactory({
          id: 200,
        }),
      })

      await userEvent.click(screen.getByTitle('Action'))
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
        }),
      })

      await userEvent.click(screen.getByTitle('Action'))
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

    it('should duplicate a template', async () => {
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
        }),
      })

      await userEvent.click(screen.getByTitle('Action'))
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
        subcategoryId: null,
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
        '/offre/collectif/202/creation?structure=3'
      )
    })
  })
})
