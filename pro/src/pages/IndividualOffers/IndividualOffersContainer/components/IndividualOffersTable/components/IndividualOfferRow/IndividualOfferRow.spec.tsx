import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import {
  ApiError,
  ListOffersOfferResponseModel,
  ListOffersStockResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { listOffersVenueFactory } from 'commons/utils/factories/collectiveApiFactories'
import {
  listOffersOfferFactory,
  listOffersStockFactory,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'

import {
  IndividualOfferRowProps,
  IndividualOfferRow,
} from './IndividualOfferRow'

vi.mock('apiClient/api', () => ({
  api: {
    deleteDraftOffers: vi.fn(),
    cancelCollectiveOfferBooking: vi.fn(),
  },
}))

const renderOfferItem = (props: IndividualOfferRowProps) =>
  renderWithProviders(
    <>
      <table>
        <tbody>
          <IndividualOfferRow {...props} />
        </tbody>
      </table>
      <Notification />
    </>
  )

const LABELS = {
  openActions: /Voir les actions/,
  deleteAction: /Supprimer l’offre/,
  eventStockEditAction: /Dates et capacités/,
  physicalStockEditAction: /Stocks/,
  deleteDraftCancel: /Annuler/,
  deleteDraftConfirm: /Supprimer/,
}

describe('IndividualOfferRow', () => {
  let props: IndividualOfferRowProps
  let offer: ListOffersOfferResponseModel
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
      isSelected: false,
      isRestrictedAsAdmin: false,
    }
  })

  describe('action buttons', () => {
    it('should display a button to show offer stocks', async () => {
      renderOfferItem(props)

      const openActionsButton = screen.getByRole('button', { name: LABELS.openActions })
      await userEvent.click(openActionsButton)

      const stockLink = screen.getByRole('menuitem', { name: LABELS.eventStockEditAction })
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

        const openActionsButton = screen.getByRole('button', { name: LABELS.openActions })
        await userEvent.click(openActionsButton)

        const deleteButton = screen.getByRole('menuitem', { name: LABELS.deleteAction })
        await userEvent.click(deleteButton)

        const deleteConfirmButton = screen.getByRole('button', { name: LABELS.deleteDraftConfirm })
        await userEvent.click(deleteConfirmButton)

        expect(api.deleteDraftOffers).toHaveBeenCalledTimes(1)
        expect(api.deleteDraftOffers).toHaveBeenCalledWith({
          ids: [offerId],
        })
        expect(
          screen.getByText('1 brouillon a bien été supprimé')
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

        const openActionsButton = screen.getByRole('button', { name: LABELS.openActions })
        await userEvent.click(openActionsButton)

        const deleteButton = screen.getByRole('menuitem', { name: LABELS.deleteAction })
        await userEvent.click(deleteButton)

        const deleteConfirmButton = screen.getByRole('button', { name: LABELS.deleteDraftConfirm })
        await userEvent.click(deleteConfirmButton)

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
          `/offre/individuelle/${offer.id}/recapitulatif/details`
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

      const offerTitleLink = screen.getByRole('link', { name: new RegExp(props.offer.name) })
      expect(offerTitleLink).toBeInTheDocument()
      expect(offerTitleLink).toHaveAttribute(
        'href',
        `/offre/individuelle/${props.offer.id}/recapitulatif/details`
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

  it('should have an edit link to detail page when offer is draft', () => {
    props.offer.status = OfferStatus.DRAFT

    renderOfferItem(props)

    const links = screen.getAllByRole('link')
    expect(links[links.length - 1]).toHaveAttribute(
      'href',
      `/offre/individuelle/${offer.id}/creation/details`
    )
  })
})
