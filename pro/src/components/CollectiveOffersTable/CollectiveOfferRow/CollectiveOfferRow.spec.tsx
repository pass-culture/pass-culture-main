import { screen, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe } from 'vitest'

import {
  CollectiveBookingStatus,
  CollectiveLocationType,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
  type CollectiveOffersStockResponseModel,
  CollectiveOfferTemplateAllowedAction,
} from '@/apiClient/v1'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { getToday } from '@/commons/utils/date'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import {
  CollectiveOfferRow,
  type CollectiveOfferRowProps,
} from './CollectiveOfferRow'

vi.mock('@/apiClient/api', () => ({
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

const offerId = 12
const stocks: Array<CollectiveOffersStockResponseModel> = [
  {
    startDatetime: String(new Date()),
    remainingQuantity: 0,
    hasBookingLimitDatetimePassed: false,
  },
]
const offer: CollectiveOfferResponseModel = collectiveOfferFactory({
  id: offerId,
  hasBookingLimitDatetimesPassed: false,
  name: 'My little offer',
  imageUrl: '/my-fake-thumb',
  stocks,
  location: { locationType: CollectiveLocationType.TO_BE_DEFINED },
})
const props: CollectiveOfferRowProps = {
  offer,
  selectOffer: vi.fn(),
  isSelected: false,
  urlSearchFilters: DEFAULT_COLLECTIVE_SEARCH_FILTERS,
  isFirstRow: true,
}

describe('CollectiveOfferRow', () => {
  describe('thumb Component', () => {
    it('should render an image with url from offer when offer has a thumb url', () => {
      renderOfferItem(props)

      expect(screen.getByRole('presentation')).toHaveAttribute(
        'src',
        '/my-fake-thumb'
      )
    })

    it('should render an image with an empty url when offer does not have a thumb url', () => {
      const offer = collectiveOfferFactory({ imageUrl: null })
      renderOfferItem({
        ...props,
        offer,
      })

      expect(
        screen.getByRole('link', {
          name: `N°${offer.id} ${offer.name}`,
        })
      ).toBeInTheDocument()
    })
  })

  describe('offer title', () => {
    it('should contain a link with the offer name and details link', () => {
      renderOfferItem(props)

      const offerTitle = screen.getByRole('link', {
        name: `N°${offerId} ${props.offer.name}`,
      })
      expect(offerTitle).toBeInTheDocument()
      expect(offerTitle).toHaveAttribute(
        'href',
        `/offre/${props.offer.id}/collectif/recapitulatif`
      )
    })

    it('should contain a link with the offer name and details link when offer is template', () => {
      renderOfferItem({ ...props, offer: { ...props.offer, isShowcase: true } })

      const offerTitle = screen.getByRole('link', {
        name: `Offre vitrine ${props.offer.name}`,
      })
      expect(offerTitle).toBeInTheDocument()
      expect(offerTitle).toHaveAttribute(
        'href',
        `/offre/T-${props.offer.id}/collectif/recapitulatif`
      )
    })
  })

  describe('offer institution', () => {
    it('should display "-" when offer is not assigned to a specific institution', () => {
      const { container } = renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({ booking: null, stocks }),
      })

      const cell = container.querySelector('td.cell-institution')

      expect(cell).toHaveTextContent('-')
    })

    it('should display institution name when offer is assigned to a specific institution', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          educationalInstitution: {
            id: 1,
            name: 'Collège Bellevue',
            city: 'Alès',
            postalCode: '30100',
            phoneNumber: '',
            institutionId: 'ABCDEF11',
          },
          stocks,
        }),
      })

      expect(screen.getByText('Collège Bellevue')).toBeInTheDocument()
      expect(screen.getByText('30100')).toBeInTheDocument()
    })

    it('should display institution cell when offer is bookable', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          educationalInstitution: {
            id: 1,
            name: 'Lycée Jean Moulin',
            city: 'Alès',
            postalCode: '30100',
            phoneNumber: '',
            institutionId: 'ABCDEF11',
            institutionType: 'LYCEE',
          },
          stocks,
        }),
      })

      expect(screen.getByText('Lycée Jean Moulin')).toBeInTheDocument()
      expect(screen.getByText('30100')).toBeInTheDocument()
    })

    it('should not display institution cell when isTemplateTable is true', () => {
      renderOfferItem({
        ...props,
        isTemplateTable: true,
      })

      expect(
        screen.queryByText('Tous les établissements')
      ).not.toBeInTheDocument()
    })
  })

  it('should display inactive thumb when offer is not editable', () => {
    renderOfferItem({
      ...props,
      offer: { ...offer, allowedActions: [], imageUrl: null },
    })

    expect(screen.getByTestId('thumb-icon')).toHaveClass('default-thumb')
  })

  it('should display disabled checkbox when offer is the offer cannot be archived', () => {
    renderOfferItem({
      ...props,
      offer: { ...offer, allowedActions: [] },
    })

    expect(screen.getByRole('checkbox')).toBeDisabled()
  })

  describe('template tag', () => {
    it('should display a tag when offer is template', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({ isShowcase: true, stocks }),
      })

      const rowHeader = screen.getAllByRole('rowheader')[0]
      expect(within(rowHeader).getByText(/Offre vitrine/i)).toBeInTheDocument()
    })

    it('should not display a tag when offer is not template', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({ isShowcase: false, stocks }),
      })

      const rowHeader = screen.getAllByRole('rowheader')[0]
      expect(
        within(rowHeader).queryByText(/Offre vitrine/i)
      ).not.toBeInTheDocument()
    })
  })

  describe('duplicate button', () => {
    it('should display confirm dialog when clicking on duplicate button when user did not see the modal', async () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          isShowcase: true,
          stocks,
          allowedActions: [
            CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
          ],
        }),
      })

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
      Storage.prototype.getItem = vi.fn(() => 'true')
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          isShowcase: true,
          stocks,
          allowedActions: [
            CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
          ],
        }),
      })

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
  })

  it('should cancel offer booking', async () => {
    renderOfferItem({
      ...props,
      offer: collectiveOfferFactory({
        stocks,
        displayedStatus: CollectiveOfferDisplayedStatus.BOOKED,
        booking: { booking_status: CollectiveBookingStatus.PENDING, id: 1 },
        allowedActions: [CollectiveOfferAllowedAction.CAN_CANCEL],
      }),
    })

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

  describe('expiration row', () => {
    it('should display a expiration row if the bookable offer is published', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          stocks: [
            {
              hasBookingLimitDatetimePassed: false,
              remainingQuantity: 1,
              bookingLimitDatetime: getToday().toISOString(),
            },
          ],
        }),
      })

      expect(
        screen.getByText('En attente de préréservation par l’enseignant')
      ).toBeInTheDocument()
    })

    it('should display a expiration row if the bookable offer is pre-booked', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
          stocks: [
            {
              hasBookingLimitDatetimePassed: false,
              remainingQuantity: 1,
              bookingLimitDatetime: getToday().toISOString(),
            },
          ],
          booking: { id: 1, booking_status: 'PENDING' },
        }),
      })

      expect(
        screen.getByText(
          'En attente de réservation par le chef d’établissement'
        )
      ).toBeInTheDocument()
    })

    it('should display a expiration row if the bookable offer is pre-booked', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
          stocks: [
            {
              hasBookingLimitDatetimePassed: false,
              remainingQuantity: 1,
              bookingLimitDatetime: getToday().toISOString(),
            },
          ],
          booking: { id: 1, booking_status: 'PENDING' },
        }),
      })

      expect(
        screen.getByText(
          'En attente de réservation par le chef d’établissement'
        )
      ).toBeInTheDocument()
    })

    it('should not display a expiration row if the offer has no booking limit', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
          stocks: [
            {
              hasBookingLimitDatetimePassed: false,
              remainingQuantity: 1,
              bookingLimitDatetime: undefined,
            },
          ],
        }),
      })

      expect(
        screen.queryByText('En attente de préréservation par l’enseignant')
      ).not.toBeInTheDocument()
    })

    it('should not display a expiration row if the offer was cancelled', () => {
      renderOfferItem({
        ...props,
        offer: collectiveOfferFactory({
          displayedStatus: CollectiveOfferDisplayedStatus.CANCELLED,
          stocks: [
            {
              hasBookingLimitDatetimePassed: false,
              remainingQuantity: 1,
              bookingLimitDatetime: getToday().toISOString(),
            },
          ],
        }),
      })

      expect(
        screen.queryByText('En attente de préréservation par l’enseignant')
      ).not.toBeInTheDocument()
    })
  })

  it('should use the creation edit URL when offer is a draft', () => {
    renderOfferItem({
      ...props,
      offer: {
        ...offer,
        displayedStatus: CollectiveOfferDisplayedStatus.DRAFT,
      },
    })

    const actionsButton = screen.getByRole('button', {
      name: 'Voir les actions',
    })
    expect(actionsButton).toBeInTheDocument()
  })

  it('should call selectOffer when checkbox is clicked', async () => {
    renderOfferItem(props)

    const checkbox = screen.getByRole('checkbox')
    await userEvent.click(checkbox)

    expect(props.selectOffer).toHaveBeenCalledWith(props.offer)
  })

  it('should apply "is-first-row" class if isFirstRow is true', () => {
    const { container } = renderOfferItem(props)

    const row = container.querySelector('tr')
    expect(row?.className).toContain('is-first-row')
  })

  it('should display "-" if educationalInstitution is null', () => {
    props.offer.educationalInstitution = null

    const { container } = renderOfferItem(props)

    const cell = container.querySelector('td.cell-institution')

    expect(cell).toHaveTextContent('-')
  })

  it('should use only the first stock for bookingLimitDate', () => {
    renderOfferItem({
      ...props,
      offer: collectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PREBOOKED,
        stocks: [
          {
            bookingLimitDatetime: getToday().toISOString(),
            remainingQuantity: 1,
            hasBookingLimitDatetimePassed: false,
          },
          {
            bookingLimitDatetime: undefined,
            remainingQuantity: 0,
            hasBookingLimitDatetimePassed: true,
          },
        ],
      }),
    })

    expect(
      screen.getByText('En attente de réservation par le chef d’établissement')
    ).toBeInTheDocument()
  })

  it('should display location cell', () => {
    renderOfferItem(props)

    expect(screen.getByText('À déterminer')).toBeInTheDocument()
  })

  it('should display price and participants cell when offer is bookable', () => {
    renderOfferItem({
      ...props,
      offer: collectiveOfferFactory({
        stocks: [
          {
            price: 10,
            numberOfTickets: 2,
            hasBookingLimitDatetimePassed: false,
          },
        ],
      }),
    })

    expect(screen.getByText('10€')).toBeInTheDocument()
    expect(screen.getByText('2 participants')).toBeInTheDocument()
  })

  it('should not display price and participants cell when isTemplateTable is true', () => {
    renderOfferItem({
      ...props,
      offer: collectiveOfferFactory({
        stocks: [
          {
            price: 10,
            numberOfTickets: 2,
            hasBookingLimitDatetimePassed: false,
          },
        ],
      }),
      isTemplateTable: true,
    })

    expect(screen.queryByText('10€')).not.toBeInTheDocument()
    expect(screen.queryByText('2 participants')).not.toBeInTheDocument()
  })
})
