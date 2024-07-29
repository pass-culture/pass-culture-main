import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  ApiError,
  CollectiveBookingStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
  ListOffersStockResponseModel,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Notification } from 'components/Notification/Notification'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import {
  collectiveOfferFactory,
  listOffersVenueFactory,
} from 'utils/collectiveApiFactories'
import { getToday } from 'utils/date'
import { listOffersStockFactory } from 'utils/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

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
  const stocks: Array<ListOffersStockResponseModel> = [
    listOffersStockFactory({
      beginningDatetime: String(new Date()),
      remainingQuantity: 0,
    }),
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
      urlSearchFilters: DEFAULT_SEARCH_FILTERS,
      isFirstRow: true,
    }
  })

  describe('thumb Component', () => {
    it('should render an image with url from offer when offer has a thumb url', () => {
      renderOfferItem(props)

      expect(
        within(
          screen.getAllByRole('link', { name: /éditer l’offre/ })[0]
        ).getByRole('img')
      ).toHaveAttribute('src', '/my-fake-thumb')
    })

    it('should render an image with an empty url when offer does not have a thumb url', () => {
      props.offer = collectiveOfferFactory({ imageUrl: null })

      renderOfferItem(props)

      expect(
        screen.getAllByTitle(`${props.offer.name} - éditer l’offre`)[0]
      ).toBeInTheDocument()
    })
  })

  describe('offer title', () => {
    it('should contain a link with the offer name and details link', () => {
      renderOfferItem(props)

      const offerTitle = screen.queryByText(props.offer.name as string, {
        selector: 'a',
      })
      expect(offerTitle).toBeInTheDocument()
      expect(offerTitle).toHaveAttribute(
        'href',
        `/offre/${props.offer.id}/collectif/recapitulatif`
      )
    })
  })

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

    expect(screen.queryByText('Gaumont - Offre numérique')).toBeInTheDocument()
  })

  describe('offer remaining quantity or institution', () => {
    it('should display "Tous les établissements" when offer is not assigned to a specific institution', () => {
      props.offer = collectiveOfferFactory({ booking: null, stocks })

      renderOfferItem(props)

      expect(screen.queryByText('Tous les établissements')).toBeInTheDocument()
    })

    it('should display "Tous les établissements" when offer is assigned to a specific institution', () => {
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

  const greyedOfferStatusDataSet = [
    CollectiveOfferStatus.REJECTED,
    CollectiveOfferStatus.PENDING,
  ]
  it.each(greyedOfferStatusDataSet)(
    'should display the offer greyed when offer is %s',
    (status) => {
      props.offer.status = status
      renderOfferItem(props)

      expect(screen.getByRole('img')).toHaveClass('thumb-inactive')
    }
  )

  const offerStatusDataSet = [
    CollectiveOfferStatus.ACTIVE,
    CollectiveOfferStatus.ARCHIVED,
  ]
  it.each(offerStatusDataSet)(
    'should not display the offer greyed when offer is %s',
    (status) => {
      props.offer.status = status
      renderOfferItem(props)

      expect(screen.getByRole('img')).not.toHaveClass('thumb-inactive')
    }
  )

  it('should display a tag when offer is template', () => {
    props.offer = collectiveOfferFactory({ isShowcase: true, stocks })
    renderOfferItem(props)

    expect(
      within(screen.getAllByRole('cell')[2]).getByText('Offre vitrine')
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
    props.offer = collectiveOfferFactory({ isShowcase: true, stocks })

    renderOfferItem(props)

    await userEvent.click(screen.getByTitle('Action'))

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
    props.offer = collectiveOfferFactory({ isShowcase: true, stocks })
    Storage.prototype.getItem = vi.fn(() => 'true')
    renderOfferItem(props)

    await userEvent.click(screen.getByTitle('Action'))

    const duplicateButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    await userEvent.click(duplicateButton)

    const modalTitle = screen.queryByLabelText('Dupliquer')
    expect(modalTitle).not.toBeInTheDocument()
  })

  it('should display booking link for sold out offer with pending booking', () => {
    props.offer = collectiveOfferFactory({
      status: CollectiveOfferStatus.SOLD_OUT,
      stocks: [
        listOffersStockFactory({
          remainingQuantity: 0,
          beginningDatetime: getToday().toISOString(),
        }),
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
      status: CollectiveOfferStatus.EXPIRED,
      stocks: [
        listOffersStockFactory({
          remainingQuantity: 0,
          beginningDatetime: getToday().toISOString(),
        }),
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
        status: CollectiveOfferStatus.SOLD_OUT,
        stocks: [
          listOffersStockFactory({
            remainingQuantity: 0,
            beginningDatetime: getToday().toISOString(),
          }),
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

  it('should cancel booking of an offer', async () => {
    props.offer = collectiveOfferFactory({
      stocks,
      status: CollectiveOfferStatus.SOLD_OUT,
      booking: { booking_status: CollectiveBookingStatus.PENDING, id: 1 },
    })
    renderOfferItem(props)

    await userEvent.click(screen.getByTitle('Action'))

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
        'La réservation sur cette offre a été annulée avec succès, votre offre sera à nouveau visible sur ADAGE.'
      )
    ).toBeInTheDocument()
  })

  it('should return an error when there are no bookings for this offer', async () => {
    props.offer = collectiveOfferFactory({
      stocks,
      status: CollectiveOfferStatus.SOLD_OUT,
      booking: { booking_status: 'PENDING', id: 0 },
    })

    vi.spyOn(api, 'cancelCollectiveOfferBooking').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        { body: { code: 'NO_BOOKING' }, status: 400 } as ApiResult,
        ''
      )
    )

    renderOfferItem(props)

    await userEvent.click(screen.getByTitle('Action'))

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

  it('should display a expiration row if the bookable offer is active, and if the FF ENABLE_COLLECTIVE_OFFERS_EXPIRATION is enabled', () => {
    props.offer = collectiveOfferFactory({
      status: CollectiveOfferStatus.ACTIVE,
      stocks: [
        {
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 1,
          bookingLimitDatetime: getToday().toISOString(),
        },
      ],
    })

    renderOfferItem(props, {
      features: ['ENABLE_COLLECTIVE_OFFERS_EXPIRATION'],
    })

    expect(
      screen.getByText('En attente de préréservation par l’enseignant')
    ).toBeInTheDocument()
  })

  it('should display a expiration row if the bookable offer is pre-booked, and if the FF ENABLE_COLLECTIVE_OFFERS_EXPIRATION is enabled', () => {
    props.offer = collectiveOfferFactory({
      status: CollectiveOfferStatus.SOLD_OUT,
      stocks: [
        {
          hasBookingLimitDatetimePassed: false,
          remainingQuantity: 1,
          bookingLimitDatetime: getToday().toISOString(),
        },
      ],
      booking: { id: 1, booking_status: 'PENDING' },
    })

    renderOfferItem(props, {
      features: ['ENABLE_COLLECTIVE_OFFERS_EXPIRATION'],
    })

    expect(
      screen.getByText('En attente de réservation par l’enseignant')
    ).toBeInTheDocument()
  })

  it('should not display a expiration row if the FF ENABLE_COLLECTIVE_OFFERS_EXPIRATION is disabled', () => {
    props.offer = collectiveOfferFactory({
      status: CollectiveOfferStatus.ACTIVE,
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

  it('should not display a expiration row if the offer has no booking limit', () => {
    props.offer = collectiveOfferFactory({
      status: CollectiveOfferStatus.ACTIVE,
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
})
