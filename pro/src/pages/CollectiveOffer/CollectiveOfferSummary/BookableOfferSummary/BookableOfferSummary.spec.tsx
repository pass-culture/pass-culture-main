import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import {
  CollectiveLocationType,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferVenueFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  BookableOfferSummary,
  type BookableOfferSummaryProps,
} from './BookableOfferSummary'

vi.mock('@/apiClient/api', () => ({
  api: {
    patchCollectiveOffersArchive: vi.fn(),
    cancelCollectiveOfferBooking: vi.fn(),
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
  const snackBarError = vi.fn()
  const snackBarSuccess = vi.fn()
  let props: BookableOfferSummaryProps
  const mockLogEvent = vi.fn()

  beforeEach(async () => {
    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
      success: snackBarSuccess,
    }))

    const offer = getCollectiveOfferFactory({
      name: 'Test Offer',
      venue: getCollectiveOfferVenueFactory({
        publicName: 'Test Venue',
        departementCode: '75',
      }),
      collectiveStock: {
        id: 1,
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

  it('should render the venue public name', () => {
    renderBookableOfferSummary(props)
    expect(screen.getByText('Proposé par Test Venue')).toBeInTheDocument()
  })

  it('should render the venue default name when venue has no public name', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        venue: getCollectiveOfferVenueFactory({
          publicName: 'Venue 1',
          name: 'Venue 1',
          departementCode: '75',
        }),
      }),
    }
    renderBookableOfferSummary(testProps)
    expect(screen.getByText('Proposé par Venue 1')).toBeInTheDocument()
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

  it('should render "0 euro" price when offer is free', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        collectiveStock: {
          id: 1,
          numberOfTickets: 50,
          price: 0,
          bookingLimitDatetime: null,
        },
      }),
    }

    renderBookableOfferSummary(testProps)
    expect(screen.getByText('0 euro')).toBeInTheDocument()
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
        },
      }),
    }
    renderBookableOfferSummary(testProps)
    expect(
      screen.getByText('Dans l’établissement scolaire')
    ).toBeInTheDocument()
  })

  it('should render the location when location type is to be defined', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        location: {
          locationType: CollectiveLocationType.TO_BE_DEFINED,
        },
      }),
    }
    renderBookableOfferSummary(testProps)
    expect(
      screen.getByText('À déterminer avec l’enseignant')
    ).toBeInTheDocument()
  })

  it('should render the date of the offer when start and end date are not the same', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        venue: getCollectiveOfferVenueFactory({
          publicName: 'Test Venue',
          departementCode: '75',
        }),
        collectiveStock: {
          id: 1,
          numberOfTickets: 50,
          price: 1000,
          startDatetime: '2023-12-21T10:00:00Z', // 11:00 in Paris (UTC+1)
          endDatetime: '2023-12-22T10:00:00Z', // 11:00 in Paris (UTC+1)
        },
      }),
    }

    renderBookableOfferSummary(testProps)
    expect(
      screen.getByText('Du 21/12/2023 au 22/12/2023 - 11h00')
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

  it('should not render the "Aperçu" action for an archived offer', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.ARCHIVED,
      }),
    }

    renderBookableOfferSummary(testProps)
    const previewButton = screen.queryByText('Aperçu')
    expect(previewButton).not.toBeInTheDocument()
  })

  it('should not render the "Aperçu" action for a draft offer', () => {
    const testProps = {
      offer: getCollectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
      }),
    }

    renderBookableOfferSummary(testProps)
    const previewButton = screen.queryByText('Aperçu')
    expect(previewButton).not.toBeInTheDocument()
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

  it('should open the confirmation modal and call the API when confirming cancellation', async () => {
    const mockCancelCollectiveOfferBooking = vi
      .spyOn(api, 'cancelCollectiveOfferBooking')
      .mockResolvedValueOnce()

    renderBookableOfferSummary(props)

    const cancelButton = screen.getByRole('button', {
      name: 'Annuler la réservation',
    })
    await userEvent.click(cancelButton)

    expect(
      screen.getByText(/Êtes-vous sûr de vouloir annuler la réservation/i)
    ).toBeInTheDocument()

    const confirmButton = screen.getByRole('button', {
      name: /Annuler la réservation/i,
    })
    await userEvent.click(confirmButton)

    expect(snackBarSuccess).toHaveBeenCalledWith(
      'Vous avez annulé la réservation de cette offre. Elle n’est donc plus visible sur ADAGE.'
    )

    await waitFor(() => {
      expect(mockCancelCollectiveOfferBooking).toHaveBeenCalledWith(
        props.offer.id
      )
    })

    expect(
      screen.queryByText(/Êtes-vous sûr de vouloir annuler la réservation/i)
    ).not.toBeInTheDocument()
  })

  it('should display an error notification if the cancellation API fails', async () => {
    vi.spyOn(api, 'cancelCollectiveOfferBooking').mockRejectedValueOnce(
      new Error('Erreur API')
    )

    renderBookableOfferSummary(props)

    const cancelButton = screen.getByText('Annuler la réservation')
    await userEvent.click(cancelButton)

    const confirmButton = screen.getByRole('button', {
      name: /Annuler la réservation/i,
    })
    await userEvent.click(confirmButton)

    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de l’annulation de la réservation.'
    )
  })

  it('should display an error notification if offer.id is missing when cancelling', async () => {
    const invalidProps = {
      ...props,
      offer: { ...props.offer, id: 0 },
    }

    renderBookableOfferSummary(invalidProps)

    const cancelButton = screen.getByText('Annuler la réservation')
    await userEvent.click(cancelButton)

    const confirmButton = screen.getByRole('button', {
      name: /Annuler la réservation/i,
    })
    await userEvent.click(confirmButton)

    expect(snackBarError).toHaveBeenCalledWith(
      'L’identifiant de l’offre n’est pas valide.'
    )
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

  it('should have the correct url for the "Retour à la liste des offres" button', () => {
    renderBookableOfferSummary(props)

    const listButton = screen.getByRole('link', {
      name: 'Retour à la liste des offres',
    })
    expect(listButton).toHaveAttribute('href', '/offres/collectives')
  })
})
