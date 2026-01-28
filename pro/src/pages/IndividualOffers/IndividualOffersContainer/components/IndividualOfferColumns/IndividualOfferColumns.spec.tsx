import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { type HeadLineOfferResponseModel, OfferStatus } from '@/apiClient/v1'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { listOffersOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import { getIndividualOfferColumns } from './IndividualOfferColumns'

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
    //id: 997,
    isVenueLocation: false,
    banId: '35288_7283_00001',
    inseeCode: '89001',
    label: 'Bureau',
    city: 'Paris',
    street: '3 rue de Valois',
    postalCode: '75001',
    isManualEdition: true,
    latitude: 48.85332,
    longitude: 2.348979,
  },
  stocks: [
    {
      remainingQuantity: 2,
      beginningDatetime: new Date().toISOString(),
      hasBookingLimitDatetimePassed: false,
      id: 0,
    },
    {
      remainingQuantity: 3,
      beginningDatetime: new Date().toISOString(),
      hasBookingLimitDatetimePassed: false,
      id: 0,
    },
  ],
})

type RenderOptions = {
  isRefactoFutureOfferEnabled?: boolean
  headlineOffer?: HeadLineOfferResponseModel | null
  isHeadlineOfferAllowedForOfferer?: boolean
}

const renderTableWithOffer = (
  offer = baseOffer,
  options: RenderOptions = {}
) => {
  const { headlineOffer = null, isHeadlineOfferAllowedForOfferer = false } =
    options

  const columns = getIndividualOfferColumns(
    headlineOffer,
    isHeadlineOfferAllowedForOfferer
  )

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
        user: { currentUser: sharedCurrentUserFactory() },
        offerer: currentOffererFactory(),
      },
    }
  )
}
describe('getIndividualOfferColumns', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
      venues: [],
    })
  })

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
      isHeadlineOfferAllowedForOfferer: true,
    })
    expect(await screen.findByText(/Offre à la une/i)).toBeInTheDocument()
  })

  it('renders bookings column if refacto feature is enabled', async () => {
    renderTableWithOffer(baseOffer, {
      isRefactoFutureOfferEnabled: true,
      headlineOffer: null,
      isHeadlineOfferAllowedForOfferer: false,
    })
    expect(await screen.findByText(/Réservations/)).toBeInTheDocument()
  })

  it('should redirect to stocks edition page when the offer is not isEvent', async () => {
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
      venues: [],
    })

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
    vi.spyOn(api, 'getVenues').mockResolvedValueOnce({
      venues: [],
    })

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
})
