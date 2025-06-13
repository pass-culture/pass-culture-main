import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  ApiError,
  CollectiveBookingStatus,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
  CollectiveOffersStockResponseModel,
  CollectiveOfferTemplateAllowedAction,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import * as useAnalytics from 'app/App/analytics/firebase'
import { CollectiveBookingsEvents } from 'commons/core/FirebaseEvents/constants'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from 'commons/core/Offers/constants'
import { getToday } from 'commons/utils/date'
import {
  collectiveOfferFactory,
  listOffersVenueFactory,
} from 'commons/utils/factories/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'

import {
  CollectiveOfferRow,
  CollectiveOfferRowProps,
} from '../CollectiveOfferRow'

vi.mock('apiClient/api', () => ({
  api: {
    deleteDraftOffers: vi.fn(),
    cancelCollectiveOfferBooking: vi.fn(),
  },
}))

const renderOfferItem = (
  props: CollectiveOfferRowProps,
  options?: RenderWithProvidersOptions
) =>
  renderWithProviders(
    <>
      <table>
        <tbody>
          <CollectiveOfferRow {...props} />
        </tbody>
      </table>
      <Notification />
    </>,
    options
  )

describe('ollectiveOfferRow', () => {
  let props: CollectiveOfferRowProps
  let offer: CollectiveOfferResponseModel
  const offerId = 12
  const stocks: Array<CollectiveOffersStockResponseModel> = [
    {
      startDatetime: String(new Date()),
      remainingQuantity: 0,
      hasBookingLimitDatetimePassed: false,
    },
  ]

  beforeEach(() => {
    offer = collectiveOfferFactory({
      id: offerId,
      hasBookingLimitDatetimesPassed: false,
      name: 'My little offer',
      imageUrl: '/my-fake-thumb',
      stocks,
    })

    props = {
      offer,
      selectOffer: vi.fn(),
      isSelected: false,
      urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
      isFirstRow: true,
    }
  })

  describe('thumb Component', () => {
    it('should render an image with url from offer when offer has a thumb url', () => {
      renderOfferItem(props)

      expect(screen.getByRole('img')).toHaveAttribute('src', '/my-fake-thumb')
    })

    it('should render an image with an empty url when offer does not have a thumb url', () => {
      props.offer = collectiveOfferFactory({ imageUrl: null })

      renderOfferItem(props)

      expect(
        screen.getAllByRole('link', { name: 'offer name 4' })[0]
      ).toBeInTheDocument()
    })
  })

  describe('offer title', () => {
    it('should contain a link with the offer name and details link', () => {
      renderOfferItem(props)

      const offerTitle = screen.getByRole('link', { name: props.offer.name })
      expect(offerTitle).toBeInTheDocument()
      expect(offerTitle).toHaveAttribute(
        'href',
        `/offre/${props.offer.id}/collectif/recapitulatif`
      )
    })
  })

  describe('venue name', () => {
    it('should display the venue name when venue public name is not given', () => {
      props.offer.venue = listOffersVenueFactory({
        name: 'Paris',
        isVirtual: false,
        offererName: 'Offerer name',
      })

      renderOfferItem(props)

      expect(screen.queryByText(props.offer.venue.name)).toBeInTheDocument()
    })

    it('should display the venue public name when is given', () => {
      props.offer.venue = listOffersVenueFactory({
        name: 'Paris',
        publicName: 'lieu de ouf',
        isVirtual: false,
        offererName: 'Offerer name',
      })

      renderOfferItem(props)

      expect(screen.queryByText('lieu de ouf')).toBeInTheDocument()
    })

    it('should display the offerer name with "- Offre numérique" when venue is virtual', () => {
      props.offer.venue = listOffersVenueFactory({
        isVirtual: true,
        name: 'Gaumont Montparnasse',
        offererName: 'Gaumont',
        publicName: 'Gaumontparnasse',
      })

      renderOfferItem(props)

      expect(
        screen.queryByText('Gaumont - Offre numérique')
      ).toBeInTheDocument()
    })
  })

  describe('offer institution', () => {
    it('should display "Tous les établissements" when offer is not assigned to a specific institution', () => {
      props.offer = collectiveOfferFactory({ booking: null, stocks })

      renderOfferItem(props)

      expect(screen.queryByText('Tous les établissements')).toBeInTheDocument()
    })

    it('should display institution name when offer is assigned to a specific institution', () => {
      props.offer = collectiveOfferFactory({
        educationalInstitution: {
          id: 1,
          name: 'Collège Bellevue',
          city: 'Alès',
          postalCode: '30100',
          phoneNumber: '',
          institutionId: 'ABCDEF11',
        },
        stocks,
      })

      renderOfferItem(props)

      expect(screen.queryByText('Collège Bellevue')).toBeInTheDocument()
    })

    it('should display acronym + city when educationalinstitution has no name', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          educationalInstitution: {
            id: 1,
            name: '',
            city: 'Alès',
            postalCode: '30100',
            phoneNumber: '',
            institutionId: 'ABCDEF11',
            institutionType: 'LYCEE',
          },
          stocks,
        }),
      })

      expect(screen.queryByText('LYCEE Alès')).toBeInTheDocument()
    })
  })

  it('should display inactive thumb when offer is not editable', () => {
    props.offer.allowedActions = [ ]
    renderOfferItem(props)

    expect(screen.getByRole('img')).toHaveClass('thumb-column-inactive')
  })

  it('should display disabled checkbox when offer is the offer cannot be archived', () => {
    props.offer.allowedActions = [ ]
    renderOfferItem(props)

    expect(screen.getByRole('checkbox')).toBeDisabled()
  })

  it('should display a tag when offer is template', () => {
    props.offer = collectiveOfferFactory({ isShowcase: true, stocks })
    renderOfferItem(props)

    expect(
      within(screen.getAllByRole('cell')[3]).getByText('Offre vitrine')
    ).toBeInTheDocument()
  })

  it('should not display a tag when offer is not template', () => {
    props.offer = collectiveOfferFactory({ isShowcase: false, stocks })
    renderOfferItem(props)

    expect(
      within(screen.getAllByRole('cell')[1]).queryByText('Offre vitrine')
    ).not.toBeInTheDocument()
  })

  it('should display confirm dialog when clicking on duplicate button when user did not see the modal', async () => {
    props.offer = collectiveOfferFactory({
      isShowcase: true,
      stocks,
      allowedActions: [
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
      ],
    })

    renderOfferItem(props)

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    const duplicateButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    await userEvent.click(duplicateButton)

    const modalTitle = screen.getByText(
      'Créer une offre réservable pour un établissement scolaire'
    )
    expect(modalTitle).toBeInTheDocument()
  })

  it('should not display confirm dialog when clicking on duplicate button when user did see the modal', async () => {
    props.offer = collectiveOfferFactory({
      isShowcase: true,
      stocks,
      allowedActions: [
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
      ],
    })
    Storage.prototype.getItem = vi.fn(() => 'true')
    renderOfferItem(props)

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    const duplicateButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    await userEvent.click(duplicateButton)

    const modalTitle = screen.queryByLabelText(
      'Créer une offre réservable pour un établissement scolaire'
    )
    expect(modalTitle).not.toBeInTheDocument()
  })

  it('should display booking link for sold out offer with pending booking', () => {
    props.offer = collectiveOfferFactory({
      displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
      stocks: [
        {
          startDatetime: String(new Date()),
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 0,
        },
      ],
      booking: { id: 1, booking_status: CollectiveBookingStatus.PENDING },
    })

    renderOfferItem(props)

    const bookingLink = screen.getByRole('link', {
      name: 'Voir la préréservation',
    })

    expect(bookingLink).toBeInTheDocument()
  })

  it('should display booking link for expired offer with booking', () => {
    props.offer = collectiveOfferFactory({
      displayedStatus: CollectiveOfferDisplayedStatus.EXPIRED,
      stocks: [
        {
          startDatetime: String(new Date()),
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 0,
        },
      ],
      booking: {
        id: 1,
        booking_status: CollectiveBookingStatus.USED,
      },
    })

    renderOfferItem(props)

    const bookingLink = screen.getByRole('link', {
      name: 'Voir la réservation',
    })

    expect(bookingLink).toBeInTheDocument()
  })

  it('should log event when clicking booking link', async () => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      ...vi.importActual('app/App/analytics/firebase'),
      logEvent: mockLogEvent,
    }))

    renderOfferItem({
      ...props,
      offer: collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
        stocks: [
          {
            startDatetime: String(new Date()),
            hasBookingLimitDatetimePassed: false,
            remainingQuantity: 0,
          },
        ],
        booking: { id: 1, booking_status: CollectiveBookingStatus.PENDING },
        id: 5,
      }),
    })

    const bookingLink = screen.getByRole('link', {
      name: 'Voir la préréservation',
    })
    await userEvent.click(bookingLink)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      CollectiveBookingsEvents.CLICKED_SEE_COLLECTIVE_BOOKING,
      {
        from: '/',
        offerId: 5,
        offerType: 'collective',
      }
    )
  })

  it('should cancel offer booking', async () => {
    props.offer = collectiveOfferFactory({
      stocks,
      displayedStatus: CollectiveOfferDisplayedStatus.BOOKED,
      booking: { booking_status: CollectiveBookingStatus.PENDING, id: 1 },
      allowedActions: [CollectiveOfferAllowedAction.CAN_CANCEL],
    })
    renderOfferItem(props)

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    const cancelBookingButton = screen.getByText('Annuler la réservation')
    await userEvent.click(cancelBookingButton)

    const modalTitle = screen.getByText(
      'Êtes-vous sûr de vouloir annuler la réservation liée à cette offre ?'
    )
    expect(modalTitle).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler la réservation' })
    )

    expect(
      screen.getByText(
        'Vous avez annulé la réservation de cette offre. Elle n’est donc plus visible sur ADAGE.'
      )
    ).toBeInTheDocument()
  })

  it('should return an error when there are no bookings for this offer', async () => {
    props.offer = collectiveOfferFactory({
      stocks,
      displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
      booking: { booking_status: 'PENDING', id: 0 },
      allowedActions: [CollectiveOfferAllowedAction.CAN_CANCEL],
    })

    vi.spyOn(api, 'cancelCollectiveOfferBooking').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        { body: { code: 'NO_BOOKING' }, status: 400 } as ApiResult,
        ''
      )
    )

    renderOfferItem(props)

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    const cancelBookingButton = screen.getByText('Annuler la réservation')
    await userEvent.click(cancelBookingButton)

    const modalTitle = screen.getByText(
      'Êtes-vous sûr de vouloir annuler la réservation liée à cette offre ?'
    )
    expect(modalTitle).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: 'Annuler la réservation' })
    )

    expect(
      screen.getByText(
        'Cette offre n’a aucune réservation en cours. Il est possible que la réservation que vous tentiez d’annuler ait déjà été utilisée.'
      )
    ).toBeInTheDocument()
  })

  describe('expiration row', () => {
    it('should display a expiration row if the bookable offer is published', () => {
      props.offer = collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        stocks: [
          {
            hasBookingLimitDatetimePassed: false,
            remainingQuantity: 1,
            bookingLimitDatetime: getToday().toISOString(),
          },
        ],
      })

      renderOfferItem(props)

      expect(
        screen.getByText('En attente de préréservation par l’enseignant')
      ).toBeInTheDocument()
    })

    it('should display a expiration row if the bookable offer is pre-booked', () => {
      props.offer = collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
        stocks: [
          {
            hasBookingLimitDatetimePassed: false,
            remainingQuantity: 1,
            bookingLimitDatetime: getToday().toISOString(),
          },
        ],
        booking: { id: 1, booking_status: 'PENDING' },
      })

      renderOfferItem(props)

      expect(
        screen.getByText(
          'En attente de réservation par le chef d’établissement'
        )
      ).toBeInTheDocument()
    })

    it('should display a expiration row if the bookable offer is pre-booked', () => {
      props.offer = collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
        stocks: [
          {
            hasBookingLimitDatetimePassed: false,
            remainingQuantity: 1,
            bookingLimitDatetime: getToday().toISOString(),
          },
        ],
        booking: { id: 1, booking_status: 'PENDING' },
      })

      renderOfferItem(props)

      expect(
        screen.getByText(
          'En attente de réservation par le chef d’établissement'
        )
      ).toBeInTheDocument()
    })

    it('should not display a expiration row if the offer has no booking limit', () => {
      props.offer = collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        stocks: [
          {
            hasBookingLimitDatetimePassed: false,
            remainingQuantity: 1,
            bookingLimitDatetime: undefined,
          },
        ],
      })

      renderOfferItem(props)

      expect(
        screen.queryByText('En attente de préréservation par l’enseignant')
      ).not.toBeInTheDocument()
    })

    it('should not display a expiration row if the offer was cancelled', () => {
      props.offer = collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.CANCELLED,
        stocks: [
          {
            hasBookingLimitDatetimePassed: false,
            remainingQuantity: 1,
            bookingLimitDatetime: getToday().toISOString(),
          },
        ],
      })

      renderOfferItem(props)

      expect(
        screen.queryByText('En attente de préréservation par l’enseignant')
      ).not.toBeInTheDocument()
    })
  })
})
