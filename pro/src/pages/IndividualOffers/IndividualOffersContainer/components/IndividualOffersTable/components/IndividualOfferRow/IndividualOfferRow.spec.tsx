import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { forwardRef } from 'react'
import { vi } from 'vitest'

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
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'
import { IndividualOffersContextProvider } from 'pages/IndividualOffers/context/IndividualOffersContext'

import {
  IndividualOfferRowProps,
  IndividualOfferRow,
} from './IndividualOfferRow'

vi.mock('apiClient/api', () => ({
  api: {
    deleteDraftOffers: vi.fn(),
    cancelCollectiveOfferBooking: vi.fn(),
    upsertHeadlineOffer: vi.fn(),
    getOffererHeadlineOffer: vi.fn(),
    deleteHeadlineOffer: vi.fn(),
    createThumbnail: vi.fn(),
  },
}))

vi.mock('react-avatar-editor', () => {
  const MockAvatarEditor = forwardRef((props, ref) => {
    if (ref && typeof ref === 'object' && 'current' in ref) {
      ref.current = {
        getImage: vi.fn(() => ({ toDataURL: vi.fn(() => 'my img') })),
        getCroppingRect: vi.fn(() => ({
          x: 0,
          y: 0,
          width: 100,
          height: 100,
        })),
      }
    }
    return ''
  })

  MockAvatarEditor.displayName = 'MockAvatarEditor'

  return {
    __esModule: true,
    default: MockAvatarEditor,
  }
})

vi.mock(
  'components/ImageUploader/components/ButtonImageEdit/ModalImageEdit/components/ModalImageUploadBrowser/ImageUploadBrowserForm/validationSchema',
  () => ({ getValidationSchema: () => ({ validate: vi.fn() }) })
)

const offererId = 1

type RenderOfferItemProps = {
  props: IndividualOfferRowProps
  isHeadlineOfferAllowedForOfferer?: boolean
  features?: string[]
}

const renderOfferItem = ({
  props,
  isHeadlineOfferAllowedForOfferer = true,
  features = [],
}: RenderOfferItemProps) =>
  renderWithProviders(
    <>
      <table>
        <tbody>
          <IndividualOffersContextProvider
            isHeadlineOfferAllowedForOfferer={isHeadlineOfferAllowedForOfferer}
          >
            <IndividualOfferRow {...props} />
          </IndividualOffersContextProvider>
        </tbody>
      </table>
      <Notification />
    </>,
    {
      storeOverrides: {
        user: { currentUser: sharedCurrentUserFactory() },
        offerer: currentOffererFactory(),
      },
      features,
    }
  )

const LABELS = {
  openActions: /Voir les actions/,
  deleteAction: /Supprimer l’offre/,
  eventStockEditAction: /Dates et capacités/,
  physicalStockEditAction: /Stocks/,
  deleteDraftCancel: /Annuler/,
  deleteDraftConfirm: /Supprimer/,
  makeHeadlineOffer: /Mettre à la une/,
  removeHeadlineOffer: /Ne plus mettre à la une/,
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
    }

    vi.spyOn(api, 'getOffererHeadlineOffer').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 404,
        } as ApiResult,
        ''
      )
    )
  })

  describe('action buttons', () => {
    it('should display a button to show offer stocks', async () => {
      renderOfferItem({ props })

      const openActionsButton = screen.getByRole('button', {
        name: LABELS.openActions,
      })
      await userEvent.click(openActionsButton)

      const stockLink = screen.getByRole('menuitem', {
        name: LABELS.eventStockEditAction,
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
        renderOfferItem({ props })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const deleteButton = screen.getByRole('menuitem', {
          name: LABELS.deleteAction,
        })
        await userEvent.click(deleteButton)

        const deleteConfirmButton = screen.getByRole('button', {
          name: LABELS.deleteDraftConfirm,
        })
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
        renderOfferItem({ props })
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

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const deleteButton = screen.getByRole('menuitem', {
          name: LABELS.deleteAction,
        })
        await userEvent.click(deleteButton)

        const deleteConfirmButton = screen.getByRole('button', {
          name: LABELS.deleteDraftConfirm,
        })
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
        renderOfferItem({ props })

        const links = screen.getAllByRole('link')
        expect(links[links.length - 1]).toHaveAttribute(
          'href',
          `/offre/individuelle/${offer.id}/recapitulatif/details`
        )
      })

      it('should not be displayed when offer is no editable', () => {
        props.offer.isEditable = false

        renderOfferItem({ props })

        const links = screen.getAllByRole('link')
        expect(links[links.length - 1]).not.toHaveAttribute(
          'href',
          `/offre/individuelle/${offer.id}/edition`
        )
      })
    })

    describe('headline offer actions', () => {
      it('should add new headline offer', async () => {
        renderOfferItem({ props, features: ['WIP_HEADLINE_OFFER'] })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const makeHeadlineOfferButton = screen.getByRole('menuitem', {
          name: LABELS.makeHeadlineOffer,
        })
        await userEvent.click(makeHeadlineOfferButton)

        expect(api.upsertHeadlineOffer).toHaveBeenCalledWith({
          offerId: offer.id,
        })
      })

      it('should handle no image case', async () => {
        const mockFile = new File(['fake img'], 'fake_img.jpg', {
          type: 'image/jpeg',
        })

        props.offer = listOffersOfferFactory({
          id: offerId,
          hasBookingLimitDatetimesPassed: false,
          name: 'My little offer without thumb',
          thumbUrl: undefined,
          stocks,
        })

        renderOfferItem({ props, features: ['WIP_HEADLINE_OFFER'] })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const makeHeadlineOfferButton = screen.getByRole('menuitem', {
          name: LABELS.makeHeadlineOffer,
        })
        await userEvent.click(makeHeadlineOfferButton)

        // dialog : add an img to make han headline offer
        expect(
          screen.getByText('Ajoutez une image pour mettre votre offre à la une')
        ).toBeInTheDocument()

        await userEvent.click(screen.getByText('Ajouter une image'))

        // dialog: import img
        const inputField = screen.getByLabelText(
          'Importer une image depuis l’ordinateur'
        )
        await userEvent.upload(inputField, mockFile)

        // dialog: crop img
        expect(screen.getByText('Modifier une image')).toBeInTheDocument()
        await userEvent.click(screen.getByText('Suivant'))

        // dialog: img preview
        expect(
          screen.getByText(
            'Prévisualisation de votre image dans l’application pass Culture'
          )
        ).toBeInTheDocument()

        await userEvent.click(screen.getByText('Enregistrer'))
        expect(api.createThumbnail).toHaveBeenCalled()

        // dialog: last step
        expect(
          screen.getByText('Votre offre va être mise à la une !')
        ).toBeInTheDocument()

        await userEvent.click(screen.getByText('Confirmer'))
        expect(api.upsertHeadlineOffer).toHaveBeenCalledWith({
          offerId: offer.id,
        })
      })

      it('should notify when img upload fails', async () => {
        vi.spyOn(api, 'createThumbnail').mockRejectedValueOnce({})

        const mockFile = new File(['fake img'], 'fake_img.jpg', {
          type: 'image/jpeg',
        })

        props.offer = listOffersOfferFactory({
          id: offerId,
          hasBookingLimitDatetimesPassed: false,
          name: 'My little offer without thumb',
          thumbUrl: undefined,
          stocks,
        })

        renderOfferItem({ props, features: ['WIP_HEADLINE_OFFER'] })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const makeHeadlineOfferButton = screen.getByRole('menuitem', {
          name: LABELS.makeHeadlineOffer,
        })
        await userEvent.click(makeHeadlineOfferButton)

        // dialog : add an img to make han headline offer
        expect(
          screen.getByText('Ajoutez une image pour mettre votre offre à la une')
        ).toBeInTheDocument()

        await userEvent.click(screen.getByText('Ajouter une image'))

        // dialog: import img
        const inputField = screen.getByLabelText(
          'Importer une image depuis l’ordinateur'
        )
        await userEvent.upload(inputField, mockFile)

        // dialog: crop img
        expect(screen.getByText('Modifier une image')).toBeInTheDocument()
        await userEvent.click(screen.getByText('Suivant'))

        // dialog: img preview
        expect(
          screen.getByText(
            'Prévisualisation de votre image dans l’application pass Culture'
          )
        ).toBeInTheDocument()

        await userEvent.click(screen.getByText('Enregistrer'))
        expect(api.createThumbnail).toHaveBeenCalled()

        expect(
          screen.getByText(
            'Une erreur est survenue lors de la sauvegarde de votre image'
          )
        ).toBeInTheDocument()
      })

      it('should notify when adding headline offer fails', async () => {
        vi.spyOn(api, 'upsertHeadlineOffer').mockRejectedValue(
          new ApiError(
            {} as ApiRequestOptions,
            {
              status: 500,
            } as ApiResult,
            ''
          )
        )
        renderOfferItem({ props, features: ['WIP_HEADLINE_OFFER'] })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const makeHeadlineOfferButton = screen.getByRole('menuitem', {
          name: LABELS.makeHeadlineOffer,
        })
        await userEvent.click(makeHeadlineOfferButton)

        expect(
          screen.getByText(
            'Une erreur s’est produite lors de l’ajout de votre offre à la une'
          )
        ).toBeInTheDocument()
      })

      it('should replace headline offer', async () => {
        vi.spyOn(api, 'getOffererHeadlineOffer').mockResolvedValue({
          id: 666,
          name: 'another headline offer',
          venueId: 1,
        })

        renderOfferItem({ props, features: ['WIP_HEADLINE_OFFER'] })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const makeHeadlineOfferButton = screen.getByRole('menuitem', {
          name: LABELS.makeHeadlineOffer,
        })
        await userEvent.click(makeHeadlineOfferButton)

        expect(
          screen.getByText(
            'Vous êtes sur le point de remplacer votre offre à la une par une nouvelle offre.'
          )
        ).toBeInTheDocument()

        await userEvent.click(screen.getByText('Confirmer'))

        expect(api.upsertHeadlineOffer).toHaveBeenCalledWith({
          offerId: offer.id,
        })
      })

      it('should delete headline offer', async () => {
        vi.spyOn(api, 'getOffererHeadlineOffer').mockResolvedValue({
          id: offer.id,
          name: offer.name,
          venueId: 1,
        })

        renderOfferItem({ props, features: ['WIP_HEADLINE_OFFER'] })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const removeHeadlineOfferButton = screen.getByRole('menuitem', {
          name: LABELS.removeHeadlineOffer,
        })
        await userEvent.click(removeHeadlineOfferButton)

        expect(api.deleteHeadlineOffer).toHaveBeenCalledWith({
          offererId,
        })
      })

      it('should notify when deleting headline offer fails', async () => {
        vi.spyOn(api, 'deleteHeadlineOffer').mockRejectedValue(
          new ApiError(
            {} as ApiRequestOptions,
            {
              status: 500,
            } as ApiResult,
            ''
          )
        )
        vi.spyOn(api, 'getOffererHeadlineOffer').mockResolvedValue({
          id: offer.id,
          name: offer.name,
          venueId: 1,
        })

        renderOfferItem({ props, features: ['WIP_HEADLINE_OFFER'] })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const removeHeadlineOfferButton = screen.getByRole('menuitem', {
          name: LABELS.removeHeadlineOffer,
        })
        await userEvent.click(removeHeadlineOfferButton)

        expect(
          screen.getByText(
            'Une erreur s’est produite lors du retrait de votre offre à la une'
          )
        ).toBeInTheDocument()
      })

      it('should not render headline actions if feature WIP_HEADLINE_OFFER is not enabled', async () => {
        renderOfferItem({ props })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const makeHeadlineOfferButton = screen.queryByRole('menuitem', {
          name: LABELS.makeHeadlineOffer,
        })

        expect(makeHeadlineOfferButton).not.toBeInTheDocument()
      })

      it('should not render headline actions if offer is not active', async () => {
        props.offer.status = OfferStatus.DRAFT

        renderOfferItem({ props, features: ['WIP_HEADLINE_OFFER'] })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const makeHeadlineOfferButton = screen.queryByRole('menuitem', {
          name: LABELS.makeHeadlineOffer,
        })

        expect(makeHeadlineOfferButton).not.toBeInTheDocument()
      })

      it('should not render headline actions if offer is digital', async () => {
        props.offer.isDigital = true

        renderOfferItem({ props, features: ['WIP_HEADLINE_OFFER'] })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const makeHeadlineOfferButton = screen.queryByRole('menuitem', {
          name: LABELS.makeHeadlineOffer,
        })

        expect(makeHeadlineOfferButton).not.toBeInTheDocument()
      })

      it('should not render headline actions if healine offer is not enabled for offerer', async () => {
        renderOfferItem({
          props,
          isHeadlineOfferAllowedForOfferer: false,
          features: ['WIP_HEADLINE_OFFER'],
        })

        const openActionsButton = screen.getByRole('button', {
          name: LABELS.openActions,
        })
        await userEvent.click(openActionsButton)

        const makeHeadlineOfferButton = screen.queryByRole('menuitem', {
          name: LABELS.makeHeadlineOffer,
        })

        expect(makeHeadlineOfferButton).not.toBeInTheDocument()
      })
    })
  })

  describe('offer title', () => {
    it('should contain a link with the offer name and details link', () => {
      renderOfferItem({ props })

      const offerTitleLink = screen.getByRole('link', {
        name: new RegExp(props.offer.name),
      })
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

    renderOfferItem({ props })

    expect(screen.queryByText(props.offer.venue.name)).toBeInTheDocument()
  })

  it('should display the venue public name when is given', () => {
    props.offer.venue = listOffersVenueFactory({
      name: 'Paris',
      publicName: 'lieu de ouf',
      isVirtual: false,
      offererName: 'Offerer name',
    })

    renderOfferItem({ props })

    expect(screen.queryByText('lieu de ouf')).toBeInTheDocument()
  })

  it('should display the offerer name with "- Offre numérique" when venue is virtual', () => {
    props.offer.venue = listOffersVenueFactory({
      isVirtual: true,
      name: 'Gaumont Montparnasse',
      offererName: 'Gaumont',
      publicName: 'Gaumontparnasse',
    })

    renderOfferItem({ props })

    expect(screen.queryByText('Gaumont - Offre numérique')).toBeInTheDocument()
  })

  it('should display the ean when given', () => {
    props.offer = listOffersOfferFactory({ productIsbn: '123456789' })

    renderOfferItem({ props })

    expect(screen.queryByText('123456789')).toBeInTheDocument()
  })

  describe('offer remaining quantity or institution', () => {
    it('should be 0 when individual offer has no stock', () => {
      renderOfferItem({ props })

      expect(screen.queryByText('0')).toBeInTheDocument()
    })

    it('should be the sum of individual offer stocks remaining quantity', () => {
      props.offer.stocks = [
        listOffersStockFactory({ remainingQuantity: 0 }),
        listOffersStockFactory({ remainingQuantity: 2 }),
        listOffersStockFactory({ remainingQuantity: 3 }),
      ]

      renderOfferItem({ props })

      expect(screen.queryByText('5')).toBeInTheDocument()
    })

    it('should be "illimité" when at least one stock of the individual offer is unlimited', () => {
      props.offer.stocks = [
        listOffersStockFactory({ remainingQuantity: 0 }),
        listOffersStockFactory({ remainingQuantity: 'unlimited' }),
      ]

      renderOfferItem({ props })

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

      renderOfferItem({ props })

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

      renderOfferItem({ props })

      expect(screen.getByText('27/05/2021 17:00')).toBeInTheDocument()
    })

    it('should not display a warning when no stocks are sold out', () => {
      props.offer.stocks = [
        listOffersStockFactory({ remainingQuantity: 'unlimited' }),
        listOffersStockFactory({ remainingQuantity: 13 }),
      ]

      renderOfferItem({ props })

      expect(screen.queryByText(/épuisée/)).not.toBeInTheDocument()
    })

    it('should not display a warning when all stocks are sold out', () => {
      props.offer.stocks = [
        listOffersStockFactory({ remainingQuantity: 0 }),
        listOffersStockFactory({ remainingQuantity: 0 }),
      ]
      offer.status = OfferStatus.SOLD_OUT

      renderOfferItem({ props })

      expect(screen.queryByText(/épuisées/)).not.toBeInTheDocument()
    })

    it('should display a warning with number of stocks sold out when at least one stock is sold out', async () => {
      props.offer.stocks = [
        listOffersStockFactory({ remainingQuantity: 0 }),
        listOffersStockFactory({ remainingQuantity: 'unlimited' }),
      ]

      renderOfferItem({ props })
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

      renderOfferItem({ props })
      await userEvent.click(screen.getAllByRole('button')[0])

      expect(
        screen.queryByText('2 dates épuisées', { selector: 'span' })
      ).toBeInTheDocument()
    })

    describe('when offer is headline', () => {
      it('should display the boosted icon', () => {
        props.offer.isHeadlineOffer = true
        renderOfferItem({
          props,
          features: ['WIP_HEADLINE_OFFER'],
        })

        expect(
          screen.getByRole('img', { name: 'Offre à la une' })
        ).toBeInTheDocument()
      })
    })
  })

  it('should have an edit link to detail page when offer is draft', () => {
    props.offer.status = OfferStatus.DRAFT

    renderOfferItem({ props })

    const links = screen.getAllByRole('link')
    expect(links[links.length - 1]).toHaveAttribute(
      'href',
      `/offre/individuelle/${offer.id}/creation/details`
    )
  })
})
