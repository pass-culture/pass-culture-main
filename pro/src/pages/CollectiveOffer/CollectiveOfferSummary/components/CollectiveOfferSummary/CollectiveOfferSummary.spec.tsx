import { screen } from '@testing-library/react'
import { expect } from 'vitest'

import {
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
  EacFormat,
  type GetVenueResponseModel,
  OfferContactFormEnum,
  VenueState,
} from '@/apiClient/v1'
import {
  getCollectiveOfferCollectiveStockFactory,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  CollectiveOfferSummary,
  type CollectiveOfferSummaryProps,
} from './CollectiveOfferSummary'

vi.mock('@/apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
    getVenue: vi.fn(),
  },
}))

const renderCollectiveOfferSummary = (
  props: CollectiveOfferSummaryProps,
  overrides?: RenderWithProvidersOptions,
  venueOverrides?: Partial<GetVenueResponseModel>
) => {
  renderWithProviders(<CollectiveOfferSummary {...props} />, {
    ...overrides,
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 1,
          ...venueOverrides,
        }),
      },
      ...overrides?.storeOverrides,
    },
  })
}

describe('CollectiveOfferSummary', () => {
  const offer = getCollectiveOfferFactory()
  const props: CollectiveOfferSummaryProps = {
    offer,
  }

  it('should show banner if generate from publicApi', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferFactory({
        isPublicApi: true,
        provider: { name: 'Mollat' },
      }),
    })
    expect(
      screen.getByText('Cette offre est synchronisée avec Mollat')
    ).toBeInTheDocument()
  })

  it('should not see edit button if offer from publicApi', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferFactory({ isPublicApi: true }),
    })

    expect(screen.queryAllByRole('link', { name: 'Modifier' })).toHaveLength(0)
  })

  it('should display national program', () => {
    renderCollectiveOfferSummary(props)
    expect(screen.getByText('Dispositif national :')).toBeInTheDocument()
    expect(screen.getByText('Collège au cinéma')).toBeInTheDocument()
  })

  it('should display format', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferFactory({
        formats: [EacFormat.PROJECTION_AUDIOVISUELLE, EacFormat.CONCERT],
      }),
    })

    expect(screen.getByText('Format :')).toBeInTheDocument()
    expect(
      screen.getByText('Projection audiovisuelle, Concert')
    ).toBeInTheDocument()
  })

  it('should display the date and time of the offer', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferTemplateFactory({
        dates: { start: '2023-10-24T09:14:00', end: '2023-10-24T09:16:00' },
      }),
    })

    const title = screen.getByRole('heading', {
      name: 'Date et heure',
    })

    expect(title).toBeInTheDocument()
  })

  it('should display the custom contact details', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferTemplateFactory({
        contactEmail: 'email@test.co',
        contactPhone: '0602030405',
        contactForm: OfferContactFormEnum.FORM,
      }),
    })

    expect(screen.getByText('email@test.co')).toBeInTheDocument()
    expect(screen.getByText('+33 6 02 03 04 05')).toBeInTheDocument()
    expect(
      screen.getByText('Le formulaire standard Pass Culture')
    ).toBeInTheDocument()
  })

  it('should display the custom contact custom url', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferTemplateFactory({
        contactUrl: 'http://www.form.com',
      }),
    })

    expect(screen.getByText('http://www.form.com')).toBeInTheDocument()
  })

  it('should not display the edition button when there is no edition link', () => {
    renderCollectiveOfferSummary({ ...props, offerEditLink: undefined })

    expect(
      screen.queryByRole('link', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })

  it('should display the edition buttons when the template offer can be edited', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS],
      }),
      offerEditLink: '123',
    })

    expect(screen.getByRole('link', { name: 'Modifier' })).toBeInTheDocument()
  })

  it('should not display the edition buttons when the template offer cannot be edited', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
      }),
      offerEditLink: '123',
    })

    expect(
      screen.queryByRole('link', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })

  it('should not display the edition buttons when the bookable offer cannot be edited', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
      }),
      offerEditLink: '123',
    })

    expect(
      screen.queryByRole('link', { name: 'Modifier' })
    ).not.toBeInTheDocument()
  })

  it('should display one edition button when the offer description is editable', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      }),
      offerEditLink: '123',
    })

    expect(screen.queryByRole('link', { name: 'Modifier' })).toBeInTheDocument()
  })

  it('should display two edition buttons when the offer description and price are editable', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
          CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT,
        ],
      }),
      offerEditLink: '123',
      stockEditLink: '234',
    })

    expect(screen.getAllByRole('link', { name: 'Modifier' })).toHaveLength(2)
  })

  it('should display two edition buttons when the offer description and dates are editable', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
          CollectiveOfferAllowedAction.CAN_EDIT_DATES,
        ],
      }),
      offerEditLink: '123',
      stockEditLink: '234',
    })

    expect(screen.getAllByRole('link', { name: 'Modifier' })).toHaveLength(2)
  })

  it('should display three edition buttons when the offer description, dates and institution are editable', () => {
    renderCollectiveOfferSummary({
      offer: getCollectiveOfferFactory({
        allowedActions: [
          CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
          CollectiveOfferAllowedAction.CAN_EDIT_DATES,
          CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION,
        ],
      }),
      offerEditLink: '123',
      stockEditLink: '234',
      institutionEditLink: '345',
    })

    expect(screen.getAllByRole('link', { name: 'Modifier' })).toHaveLength(3)
  })

  it('should not display any edition button when the selected venue is closed', () => {
    renderCollectiveOfferSummary(
      {
        offer: getCollectiveOfferFactory({
          allowedActions: [
            CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
            CollectiveOfferAllowedAction.CAN_EDIT_DATES,
            CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION,
          ],
        }),
        offerEditLink: '123',
        stockEditLink: '234',
        institutionEditLink: '345',
      },
      undefined,
      { state: VenueState.CLOSED }
    )

    expect(screen.queryAllByRole('link', { name: 'Modifier' })).toHaveLength(0)
  })

  describe('WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS', () => {
    const ffOverrides: RenderWithProvidersOptions = {
      features: ['WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'],
    }

    it('should display the 4 main sections for a bookable offer', () => {
      renderCollectiveOfferSummary(
        { offer: getCollectiveOfferFactory() },
        ffOverrides
      )

      expect(
        screen.getByRole('heading', { name: 'Détails de l’offre' })
      ).toBeVisible()
      expect(
        screen.getByRole('heading', { name: 'Dates et prix' })
      ).toBeVisible()
      expect(
        screen.getByRole('heading', {
          name: 'Informations pratiques',
          level: 2,
        })
      ).toBeVisible()
      expect(
        screen.getByRole('heading', { name: 'Établissement et enseignant' })
      ).toBeVisible()
    })

    it('should display priceDetail in "Informations pratiques" when it exists', () => {
      renderCollectiveOfferSummary(
        {
          offer: getCollectiveOfferFactory({
            collectiveStock: getCollectiveOfferCollectiveStockFactory({
              priceDetail: 'Détail du prix pratique',
            }),
          }),
        },
        ffOverrides
      )

      const heading = screen.getByRole('heading', {
        name: 'Informations pratiques',
        level: 2,
      })
      const priceDetailElement = screen.getByText('Détail du prix pratique')
      expect(priceDetailElement).toBeInTheDocument()
      expect(heading.closest('.summary-layout-section')).toContainElement(
        priceDetailElement
      )
    })

    it('should not display priceDetail subsection when priceDetail is null', () => {
      renderCollectiveOfferSummary(
        {
          offer: getCollectiveOfferFactory({
            collectiveStock: getCollectiveOfferCollectiveStockFactory({
              priceDetail: null,
            }),
          }),
        },
        ffOverrides
      )

      expect(
        screen.queryByText('Détail du prix pratique')
      ).not.toBeInTheDocument()
    })

    it('should display notification section when bookingEmails exist', () => {
      renderCollectiveOfferSummary(
        {
          offer: getCollectiveOfferFactory({
            bookingEmails: ['test-booking-email@example.com'],
          }),
        },
        ffOverrides
      )
      expect(
        screen.queryByRole('heading', { name: 'Dates et prix' })
      ).toBeVisible()
      expect(screen.getByText('test-booking-email@example.com')).toBeVisible()
    })

    it('should not display notification section when bookingEmails is empty', () => {
      renderCollectiveOfferSummary(
        {
          offer: getCollectiveOfferFactory({
            bookingEmails: [],
          }),
        },
        ffOverrides
      )

      expect(
        screen.queryByText('Notifications des réservations :')
      ).not.toBeInTheDocument()
    })

    it('should fall back to old layout for a template offer', () => {
      renderCollectiveOfferSummary(
        { offer: getCollectiveOfferTemplateFactory() },
        ffOverrides
      )

      expect(
        screen.queryByRole('heading', { name: 'Dates et prix' })
      ).not.toBeInTheDocument()
    })
  })
})
