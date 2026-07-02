import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { type HeadLineOfferResponseModel, OfferStatus } from '@/apiClient/v1'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import {
  Events,
  INDIVIDUAL_OFFERS_NAVIGATION_SOURCE,
} from '@/commons/core/FirebaseEvents/constants'
import { listOffersOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import { getIndividualOfferColumns } from './IndividualOfferColumns'

const mockLogEvent = vi.fn()
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: mockLogEvent }),
}))

const headlineOffer: HeadLineOfferResponseModel = {
  id: 123,
  name: 'Headline offer',
  venueId: 1,
}

const baseOffer = listOffersOfferFactory({
  id: 123,
  name: 'My Offer',
  status: OfferStatus.ACTIVE,
  thumbUrl: '/image.png',
  location: {
    id: 1,
    isVenueLocation: false,
    banId: '35288_7283_00001',
    inseeCode: '89001',
    label: 'Bureau',
    city: 'Paris',
    street: '3 rue de Valois',
    postalCode: '75001',
    departmentCode: '75',
    isManualEdition: true,
    latitude: 48.85332,
    longitude: 2.348979,
  },
  stocks: [
    {
      remainingQuantity: 2,
      beginningDatetime: new Date().toISOString(),
      id: 0,
    },
    {
      remainingQuantity: 3,
      beginningDatetime: new Date().toISOString(),
      id: 0,
    },
  ],
})

type RenderOptions = {
  isRefactoFutureOfferEnabled?: boolean
  headlineOffer?: HeadLineOfferResponseModel | null
  isOfferExposureEnabled?: boolean
  isReadOnly?: boolean
}

const renderTableWithOffer = (
  offer = baseOffer,
  options: RenderOptions = {}
) => {
  const {
    headlineOffer = null,
    isOfferExposureEnabled = false,
    isReadOnly = false,
  } = options

  const columns = getIndividualOfferColumns({
    headlineOffer,
    isOfferExposureEnabled,
    isReadOnly,
  })

  return renderWithProviders(
    <HeadlineOfferContextProvider>
      <Table
        columns={columns}
        data={[offer]}
        isLoading={false}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: '',
          onFilterReset: () => {
            throw new Error('Function not implemented.')
          },
        }}
        noData={{
          hasNoData: false,
          message: {
            icon: '',
            title: '',
            subtitle: '',
          },
        }}
      />
    </HeadlineOfferContextProvider>,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
        },
      },
    }
  )
}
describe('getIndividualOfferColumns', () => {
  it('renders location based on address', async () => {
    renderTableWithOffer()
    expect(
      await screen.findByText(/Bureau - 3 rue de Valois 75001 Paris/i)
    ).toBeInTheDocument()
  })

  it('renders total stock quantity', async () => {
    renderTableWithOffer()
    expect(await screen.findByText('5')).toBeInTheDocument()
  })

  it('renders "Illimité" if at least one stock is unlimited', async () => {
    const offer = {
      ...baseOffer,
      stocks: [
        {
          id: 1,
          remainingQuantity: 'unlimited',
          beginningDatetime: new Date().toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
        {
          id: 2,
          remainingQuantity: 2,
          beginningDatetime: new Date().toISOString(),
          hasBookingLimitDatetimePassed: false,
        },
      ],
    }
    renderTableWithOffer(offer)
    expect(await screen.findByText('Illimité')).toBeInTheDocument()
  })

  it('displays boosted icon when offer is headline', async () => {
    renderTableWithOffer(baseOffer, {
      isRefactoFutureOfferEnabled: false,
      headlineOffer,
    })
    expect(await screen.findByText(/Offre à la une/i)).toBeInTheDocument()
  })

  it('renders bookings column if refacto feature is enabled', async () => {
    renderTableWithOffer(baseOffer, {
      isRefactoFutureOfferEnabled: true,
      headlineOffer: null,
    })
    expect(await screen.findByText(/Réservations/)).toBeInTheDocument()
  })

  it('should redirect to stocks edition page when the offer is not isEvent', async () => {
    renderTableWithOffer({ ...baseOffer, isEvent: false }, {})

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    expect(screen.getByRole('link', { name: 'Stocks' })).toHaveAttribute(
      'href',
      expect.stringContaining('/edition/tarifs')
    )
  })

  it('should redirect to timetable edition page when the offer is isEvent', async () => {
    renderTableWithOffer(
      {
        ...baseOffer,
        isEvent: true,
      },
      {}
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )

    expect(
      screen.getByRole('link', { name: 'Dates et capacités' })
    ).toHaveAttribute('href', expect.stringContaining('/edition/horaires'))
  })

  it('should link to exposure when feature is enabled', async () => {
    renderTableWithOffer(baseOffer, { isOfferExposureEnabled: true })

    expect(
      await screen.findByRole('link', { name: 'My Offer 2 dates' })
    ).toHaveAttribute('href', expect.stringContaining('/visibilite'))
  })

  it('should keep creation link for draft when feature is enabled', async () => {
    renderTableWithOffer(
      { ...baseOffer, status: OfferStatus.DRAFT },
      { isOfferExposureEnabled: true }
    )

    expect(
      await screen.findByRole('link', { name: 'My Offer 2 dates' })
    ).toHaveAttribute('href', expect.stringContaining('/creation/description'))
  })

  it('should include the actions column when isReadOnly is false', () => {
    const columns = getIndividualOfferColumns({
      headlineOffer: null,
      isOfferExposureEnabled: false,
      isReadOnly: false,
    })

    expect(columns.map((column) => column.id)).toContain('actions')
  })

  it('should log source tracker on offer redirection link', async () => {
    renderTableWithOffer({ ...baseOffer, isEvent: false }, {})

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )
    await userEvent.click(screen.getByRole('link', { name: 'Voir l’offre' }))

    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        used: INDIVIDUAL_OFFERS_NAVIGATION_SOURCE.ACTIONS_MENU_VIEW_OFFER,
        offerId: 123,
      }
    )
  })

  it('should log source tracker on offer edit redirection link', async () => {
    renderTableWithOffer({ ...baseOffer, isEvent: false }, {})

    await userEvent.click(
      screen.getByRole('button', { name: 'Voir les actions' })
    )
    await userEvent.click(screen.getByRole('link', { name: 'Stocks' }))

    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        used: INDIVIDUAL_OFFERS_NAVIGATION_SOURCE.ACTIONS_MENU_EDIT_OFFER_STOCK,
        offerId: 123,
      }
    )
  })

  it('should omit the actions column when isReadOnly is true', async () => {
    renderTableWithOffer(baseOffer, { isReadOnly: true })

    expect(await screen.findByText('My Offer')).toBeVisible()
    expect(
      screen.queryByRole('button', { name: 'Voir les actions' })
    ).not.toBeInTheDocument()

    const columns = getIndividualOfferColumns({
      headlineOffer: null,
      isOfferExposureEnabled: false,
      isReadOnly: true,
    })
    expect(columns.map((column) => column.id)).not.toContain('actions')
  })
})
