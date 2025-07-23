import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  CollectiveLocationType,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
} from 'apiClient/v1'
import * as useAnalytics from 'app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from 'commons/core/FirebaseEvents/constants'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferVenueFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import {
  BookableOfferSummary,
  BookableOfferSummaryProps,
} from './BookableOfferSummary'

vi.mock('apiClient/api', () => ({
  api: {
    patchCollectiveOffersArchive: vi.fn(),
  },
}))

const renderBookableOfferSummary = (
  props: BookableOfferSummaryProps,
  options?: RenderWithProvidersOptions
) =>
  renderWithProviders(<BookableOfferSummary {...props} />, {
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory(),
    },
    ...options,
  })

describe('BookableOfferSummary', () => {
  let props: BookableOfferSummaryProps
  const mockLogEvent = vi.fn()

  beforeEach(() => {
    const offer = getCollectiveOfferFactory({
      name: 'Test Offer',
      venue: getCollectiveOfferVenueFactory({ publicName: 'Test Venue', departementCode: '75' }),
      collectiveStock: {
        id: 1,
        isBooked: false,
        isCancellable: true,
        numberOfTickets: 50,
        price: 1000,
        startDatetime: '2023-12-21T10:00:00Z',
        endDatetime: '2023-12-21T10:00:00Z',
        bookingLimitDatetime: '2023-12-31T22:59:59Z',
      },
      allowedActions: [
        CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
        CollectiveOfferAllowedAction.CAN_DUPLICATE,
        CollectiveOfferAllowedAction.CAN_ARCHIVE,
        CollectiveOfferAllowedAction.CAN_CANCEL,
      ],
      displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
    })
    props = { offer }
  })

  it('should render the offer name', () => {
    renderBookableOfferSummary(props)
    expect(screen.getByText('Test Offer')).toBeInTheDocument()
  })

  it('should render the venue name', () => {
    renderBookableOfferSummary(props)
    expect(screen.getByText('Proposé par Test Venue')).toBeInTheDocument()
  })

  it('should render the number of participants', () => {
    renderBookableOfferSummary(props)
    expect(screen.getByText('50 participants')).toBeInTheDocument()
  })

  it("should render default recap value when value doesn't exist", () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        collectiveStock: {
          id: 1,
          isBooked: false,
          isCancellable: true,
          numberOfTickets: null,
          price: 1000,
          bookingLimitDatetime: null,
        },
      }),
    }

    renderBookableOfferSummary(testProps)
    expect(screen.getAllByText('-')).toHaveLength(3)
  })

  it('should render the price', () => {
    renderBookableOfferSummary(props)
    expect(screen.getByText('1000 euros')).toBeInTheDocument()
  })

  it('should render the booking limit date', () => {
    renderBookableOfferSummary(props)
    expect(
      screen.getByText('Date limite de réservation : 31/12/2023')
    ).toBeInTheDocument()
  })

  it('should render the location when location type is school', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        location: {
          locationType: CollectiveLocationType.SCHOOL,
        }
      })
    }
    renderBookableOfferSummary(testProps, {
      features: ['WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'],
    })
    expect(
      screen.getByText('Dans l’établissement scolaire')
    ).toBeInTheDocument()
  })

  it('should render the location when location type is to be defined', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,
        }
      })
    }
    renderBookableOfferSummary(testProps, {
      features: ['WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'],
    })
    expect(
      screen.getByText('À déterminer avec l’enseignant')
    ).toBeInTheDocument()
  })

  it('should render the date of the offer when start and end date are not the same', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        venue: getCollectiveOfferVenueFactory({ publicName: 'Test Venue', departementCode: '75' }),
        collectiveStock: {
          id: 1,
          isBooked: false,
          isCancellable: true,
          numberOfTickets: 50,
          price: 1000,
          startDatetime: '2023-12-21T10:00:00Z', // 11:00 in Paris (UTC+1)
          endDatetime: '2023-12-22T10:00:00Z', // 11:00 in Paris (UTC+1)
        },
      }),
    }

    renderBookableOfferSummary(testProps)
    expect(
      screen.getByText("Du 21/12/2023 au 22/12/2023 - 11h00")
    ).toBeInTheDocument()
  })

  it('should render the "Modifier" action if editing is allowed', () => {
    renderBookableOfferSummary(props)
    const editButton = screen.getByLabelText('Modifier l’offre')
    expect(editButton).toBeInTheDocument()
  })

  it('should render the "Aperçu" action', () => {
    renderBookableOfferSummary(props)
    const previewButton = screen.getByText('Aperçu')
    expect(previewButton).toBeInTheDocument()
  })

  it('should render the "Aperçu" action for an archived offer', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.ARCHIVED,
      }),
    }

    renderBookableOfferSummary(testProps)
    const previewButton = screen.getByText('Aperçu')
    expect(previewButton).toBeInTheDocument()
  })

  it('should render the "Dupliquer" action if duplication is allowed', () => {
    renderBookableOfferSummary(props)
    const duplicateButton = screen.getByText('Dupliquer')
    expect(duplicateButton).toBeInTheDocument()
  })

  it('should call the API to archive the offer when confirming in the modal', async () => {
    const mockPatchCollectiveOffersArchive = vi
      .spyOn(api, 'patchCollectiveOffersArchive')
      .mockResolvedValueOnce()

    renderWithProviders(<BookableOfferSummary {...props} />)

    const archiveButton = screen.getByText('Archiver')
    expect(archiveButton).toBeInTheDocument()

    await userEvent.click(archiveButton)

    const confirmButton = screen.getByText('Archiver l’offre')
    expect(
      screen.getByText('Êtes-vous sûr de vouloir archiver cette offre ?')
    ).toBeInTheDocument()

    await userEvent.click(confirmButton)

    await waitFor(() => {
      expect(mockPatchCollectiveOffersArchive).toHaveBeenCalledWith({
        ids: [props.offer.id],
      })
    })

    expect(
      screen.queryByText('Êtes-vous sûr de vouloir archiver cette offre ?')
    ).not.toBeInTheDocument()
  })

  it('should render the "Annuler la réservation" action if cancellation is allowed', () => {
    renderBookableOfferSummary(props)
    const cancelButton = screen.getByText('Annuler la réservation')
    expect(cancelButton).toBeInTheDocument()
  })

  it('should log event when clicking "Dupliquer" button', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderBookableOfferSummary(props)

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
        offerId: props.offer.id,
        offerType: 'collective',
        offerStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      }
    )
  })
})
