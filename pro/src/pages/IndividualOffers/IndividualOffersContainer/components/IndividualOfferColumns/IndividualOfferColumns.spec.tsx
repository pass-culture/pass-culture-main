import { screen } from '@testing-library/react'

import { HeadLineOfferResponseModel, OfferStatus } from '@/apiClient/v1'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { listOffersOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Table, TableVariant } from '@/ui-kit/Table/Table'

import { getIndividualOfferColumns } from './IndividualOfferColumns'

describe('getIndividualOfferColumns', () => {
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
    address: {
      id: 1,
      id_oa: 997,
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
    const {
      isRefactoFutureOfferEnabled = false,
      headlineOffer = null,
      isHeadlineOfferAllowedForOfferer = false,
    } = options

    const columns = getIndividualOfferColumns(
      isRefactoFutureOfferEnabled,
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

  it('renders offer name with link', () => {
    renderTableWithOffer()
    expect(screen.getByRole('link', { name: /My Offer/i })).toHaveAttribute(
      'href',
      '/offre/individuelle/123/recapitulatif/details'
    )
  })

  it('renders location based on address', () => {
    renderTableWithOffer()
    expect(
      screen.getByText(/Bureau - 3 rue de Valois 75001 Paris/i)
    ).toBeInTheDocument()
  })

  it('renders total stock quantity', () => {
    renderTableWithOffer()
    expect(screen.getByText('5')).toBeInTheDocument()
  })

  it('renders "Illimité" if at least one stock is unlimited', () => {
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
    expect(screen.getByText('Illimité')).toBeInTheDocument()
  })

  it('displays boosted icon when offer is headline', () => {
    renderTableWithOffer(baseOffer, {
      isRefactoFutureOfferEnabled: false,
      headlineOffer,
      isHeadlineOfferAllowedForOfferer: true,
    })
    expect(screen.getByText(/Offre à la une/i)).toBeInTheDocument()
  })

  it('renders bookings column if refacto feature is enabled', () => {
    renderTableWithOffer(baseOffer, {
      isRefactoFutureOfferEnabled: true,
      headlineOffer: null,
      isHeadlineOfferAllowedForOfferer: false,
    })
    expect(screen.getByText(/Réservations/)).toBeInTheDocument()
  })
})
