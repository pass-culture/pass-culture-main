import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  ApiError,
  CollectiveBookingStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
  ListOffersOfferResponseModel,
  ListOffersStockResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Notification } from 'components/Notification/Notification'
import { CollectiveBookingsEvents } from 'core/FirebaseEvents/constants'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Audience } from 'core/shared/types'
import {
  collectiveOfferFactory,
  listOffersVenueFactory,
} from 'utils/collectiveApiFactories'
import { getToday } from 'utils/date'
import {
  listOffersOfferFactory,
  listOffersStockFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { OfferItem, OfferItemProps } from '../OfferItem'

vi.mock('apiClient/api', () => ({
  api: {
    deleteDraftOffers: vi.fn(),
    cancelCollectiveOfferBooking: vi.fn(),
  },
}))

const renderOfferItem = (props: OfferItemProps) =>
  renderWithProviders(
    <>
      <table>
        <tbody>
          <OfferItem {...props} />
        </tbody>
      </table>
      <Notification />
    </>,
    {
      storeOverrides: {
        user: { currentUser: sharedCurrentUserFactory(), selectedOffererId: 1 },
      },
    }
  )

describe('src | components | pages | Offers | OfferItem', () => {
  let props: OfferItemProps
  let offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  const offerId = 12
  const stocks: Array<ListOffersStockResponseModel> = [
    listOffersStockFactory({
      beginningDatetime: String(new Date()),
      remainingQuantity: 0,
    }),
  ]

  beforeEach(() => {
    offer = listOffersOfferFactory({
      id: offerId,
      hasBookingLimitDatetimesPassed: false,
      name: 'My little offer',
      thumbUrl: '/my-fake-thumb',
      stocks,
    })

    props = {
      offer,
      selectOffer: vi.fn(),
      audience: Audience.INDIVIDUAL,
      urlSearchFilters: DEFAULT_SEARCH_FILTERS,
    }
  })

  describe('render', () => {
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
        props.offer = listOffersOfferFactory({ thumbUrl: null })

        renderOfferItem(props)

        expect(
          screen.getAllByTitle(`${props.offer.name} - éditer l’offre`)[0]
        ).toBeInTheDocument()
      })
    })

    describe('action buttons', () => {
      it('should display a button to show offer stocks', () => {
        renderOfferItem(props)

        const stockLink = screen.getByRole('link', {
          name: 'Dates et capacités',
        })
        expect(stockLink).toBeInTheDocument()
        expect(stockLink).toHaveAttribute(
          'href',
          `/offre/individuelle/${offer.id}/edition/stocks`
        )
      })
      describe('draft delete button', () => {
        it('should display a trash icon with a confirm dialog to delete draft offer', async () => {
          props.offer.status = OfferStatus.DRAFT

          renderOfferItem(props)

          await userEvent.click(screen.getAllByRole('button')[1])
          const deleteButton = screen.getByRole('button', {
            name: 'Supprimer ce brouillon',
          })
          await userEvent.click(deleteButton)
          expect(api.deleteDraftOffers).toHaveBeenCalledTimes(1)
          expect(api.deleteDraftOffers).toHaveBeenCalledWith({
            ids: [offerId],
          })
          expect(
            screen.getByText('Le brouillon a bien été supprimé')
          ).toBeInTheDocument()
        })

        it('should display a notification in case of draft deletion error', async () => {
          props.offer.status = OfferStatus.DRAFT

          renderOfferItem(props)
          vi.spyOn(api, 'deleteDraftOffers').mockRejectedValue(
            new ApiError(
              {} as ApiRequestOptions,
              {
                status: 500,
                body: {
                  ids: 'api wrong ids',
                },
              } as ApiResult,
              ''
            )
          )

          await userEvent.click(screen.getAllByRole('button')[1])
          await userEvent.click(
            screen.getByRole('button', {
              name: 'Supprimer ce brouillon',
            })
          )
          expect(api.deleteDraftOffers).toHaveBeenCalledTimes(1)
          expect(api.deleteDraftOffers).toHaveBeenCalledWith({
            ids: [offerId],
          })
          expect(
            screen.getByText(
              'Une erreur est survenue lors de la suppression du brouillon'
            )
          ).toBeInTheDocument()
        })
      })

      describe('edit offer link', () => {
        it('should be displayed when offer is editable', () => {
          renderOfferItem(props)

          const links = screen.getAllByRole('link')
          expect(links[links.length - 1]).toHaveAttribute(
            'href',
            `/offre/individuelle/${offer.id}/recapitulatif`
          )
        })

        it('should not be displayed when offer is no editable', () => {
          props.offer.isEditable = false

          renderOfferItem(props)

          const links = screen.getAllByRole('link')
          expect(links[links.length - 1]).not.toHaveAttribute(
            'href',
            `/offre/individuelle/${offer.id}/edition`
          )
        })
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
          `/offre/individuelle/${props.offer.id}/recapitulatif`
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

      expect(
        screen.queryByText('Gaumont - Offre numérique')
      ).toBeInTheDocument()
    })

    it('should display the ean when given', () => {
      props.offer = listOffersOfferFactory({ productIsbn: '123456789' })

      renderOfferItem(props)

      expect(screen.queryByText('123456789')).toBeInTheDocument()
    })

    describe('offer remaining quantity or institution', () => {
      it('should be 0 when individual offer has no stock', () => {
        renderOfferItem(props)

        expect(screen.queryByText('0')).toBeInTheDocument()
      })

      it('should be the sum of individual offer stocks remaining quantity', () => {
        props.offer.stocks = [
          listOffersStockFactory({ remainingQuantity: 0 }),
          listOffersStockFactory({ remainingQuantity: 2 }),
          listOffersStockFactory({ remainingQuantity: 3 }),
        ]

        renderOfferItem(props)

        expect(screen.queryByText('5')).toBeInTheDocument()
      })

      it('should be "illimité" when at least one stock of the individual offer is unlimited', () => {
        props.offer.stocks = [
          listOffersStockFactory({ remainingQuantity: 0 }),
          listOffersStockFactory({ remainingQuantity: 'unlimited' }),
        ]

        renderOfferItem(props)

        expect(screen.queryByText('Illimité')).toBeInTheDocument()
      })

      it('should display "Tous les établissements" when offer is collective and is not assigned to a specific institution', () => {
        props.audience = Audience.COLLECTIVE
        props.offer = collectiveOfferFactory({ booking: null, stocks })

        renderOfferItem(props)

        expect(
          screen.queryByText('Tous les établissements')
        ).toBeInTheDocument()
      })

      it('should display "Tous les établissements" when offer is collective and is assigned to a specific institution', () => {
        props.audience = Audience.COLLECTIVE
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

      it('should display acronym + city when offer is collective and educationalinstitution has no name', () => {
        renderOfferItem({
          ...props,
          audience: Audience.COLLECTIVE,
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

    describe('when offer is an event product', () => {
      it('should display the correct text "2 dates"', () => {
        props.offer.venue = listOffersVenueFactory({ departementCode: '973' })
        props.offer.stocks = [
          listOffersStockFactory({
            beginningDatetime: '01-01-2001',
            remainingQuantity: 'unlimited',
          }),
          listOffersStockFactory({
            beginningDatetime: '01-01-2001',
            remainingQuantity: 'unlimited',
          }),
        ]

        renderOfferItem(props)

        expect(screen.queryByText('2 dates')).toBeInTheDocument()
      })

      it('should display the beginning date time when only one date', () => {
        props.offer.venue = listOffersVenueFactory({ departementCode: '973' })
        props.offer.stocks = [
          listOffersStockFactory({
            beginningDatetime: '2021-05-27T20:00:00Z',
            remainingQuantity: 10,
          }),
        ]

        renderOfferItem(props)

        expect(screen.getByText('27/05/2021 17:00')).toBeInTheDocument()
      })

      it('should not display a warning when no stocks are sold out', () => {
        props.offer.stocks = [
          listOffersStockFactory({ remainingQuantity: 'unlimited' }),
          listOffersStockFactory({ remainingQuantity: 13 }),
        ]

        renderOfferItem(props)

        expect(screen.queryByText(/épuisée/)).not.toBeInTheDocument()
      })

      it('should not display a warning when all stocks are sold out', () => {
        props.offer.stocks = [
          listOffersStockFactory({ remainingQuantity: 0 }),
          listOffersStockFactory({ remainingQuantity: 0 }),
        ]
        offer.status = OfferStatus.SOLD_OUT

        renderOfferItem(props)

        expect(screen.queryByText(/épuisées/)).not.toBeInTheDocument()
      })

      it('should display a warning with number of stocks sold out when at least one stock is sold out', async () => {
        props.offer.stocks = [
          listOffersStockFactory({ remainingQuantity: 0 }),
          listOffersStockFactory({ remainingQuantity: 'unlimited' }),
        ]

        renderOfferItem(props)
        await userEvent.click(screen.getAllByRole('button')[0])

        const numberOfStocks = screen.getByText('1 date épuisée', {
          selector: 'span',
        })
        expect(numberOfStocks).toBeInTheDocument()
      })

      it('should pluralize number of stocks sold out when at least two stocks are sold out', async () => {
        props.offer.stocks = [
          listOffersStockFactory({ remainingQuantity: 0 }),
          listOffersStockFactory({ remainingQuantity: 0 }),
          listOffersStockFactory({ remainingQuantity: 12 }),
        ]

        renderOfferItem(props)
        await userEvent.click(screen.getAllByRole('button')[0])

        expect(
          screen.queryByText('2 dates épuisées', { selector: 'span' })
        ).toBeInTheDocument()
      })
    })

    it('should display the offer greyed when offer is inactive', () => {
      props.offer.isActive = false

      renderOfferItem(props)

      expect(
        screen.getByLabelText('My little offer').closest('tr')
      ).toHaveClass('inactive')
    })

    const greyedOfferStatusDataSet = [OfferStatus.REJECTED, OfferStatus.PENDING]
    it.each(greyedOfferStatusDataSet)(
      'should display the offer greyed when offer is %s',
      (status) => {
        props.offer.status = status
        renderOfferItem(props)

        expect(
          screen.getByLabelText('My little offer').closest('tr')
        ).toHaveClass('inactive')
      }
    )

    const offerStatusDataSet = [OfferStatus.ACTIVE, OfferStatus.DRAFT]
    it.each(offerStatusDataSet)(
      'should not display the offer greyed when offer is %s',
      (status) => {
        props.offer.status = status
        renderOfferItem(props)

        expect(
          screen.getByLabelText('My little offer').closest('tr')
        ).not.toHaveClass('inactive')
      }
    )

    it('should have an edit link to detail page when offer is draft', () => {
      props.offer.status = OfferStatus.DRAFT

      renderOfferItem(props)

      const links = screen.getAllByRole('link')
      expect(links[links.length - 1]).toHaveAttribute(
        'href',
        `/offre/individuelle/${offer.id}/creation/informations`
      )
    })

    describe('when audience is COLLECTIVE', () => {
      it('should display a tag when offer is template', () => {
        props.audience = Audience.COLLECTIVE
        props.offer = collectiveOfferFactory({ isShowcase: true, stocks })
        renderOfferItem(props)

        expect(
          within(screen.getAllByRole('cell')[2]).getByText('Offre vitrine')
        ).toBeInTheDocument()
      })

      it('should not display a tag when offer is not template', () => {
        props.audience = Audience.COLLECTIVE
        props.offer = collectiveOfferFactory({ isShowcase: false, stocks })
        renderOfferItem(props)

        expect(
          within(screen.getAllByRole('cell')[1]).queryByText('Offre vitrine')
        ).not.toBeInTheDocument()
      })

      it('should display confirm dialog when clicking on duplicate button when user did not see the modal', async () => {
        props.audience = Audience.COLLECTIVE
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
        props.audience = Audience.COLLECTIVE
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
        props.audience = Audience.COLLECTIVE
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
    })

    it('should display booking link for expired offer with booking', () => {
      props.audience = Audience.COLLECTIVE
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
        audience: Audience.COLLECTIVE,
        offer: collectiveOfferFactory({
          status: CollectiveOfferStatus.SOLD_OUT,
          stocks: [
            listOffersStockFactory({
              remainingQuantity: 0,
              beginningDatetime: getToday().toISOString(),
            }),
          ],
          booking: { id: 1, booking_status: CollectiveBookingStatus.PENDING },
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
          offerId: 10,
          offerType: 'collective',
          offererId: '1',
        }
      )
    })

    it('should cancel booking of an offer', async () => {
      props.audience = Audience.COLLECTIVE
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
      props.audience = Audience.COLLECTIVE
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
  })
})
