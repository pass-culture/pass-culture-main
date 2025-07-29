import { screen } from '@testing-library/react'

import { HeadLineOfferResponseModel, OfferStatus } from 'apiClient/v1'
import { HeadlineOfferContextProvider } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { listOffersOfferFactory } from 'commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Table, TableVariant } from 'ui-kit/Table/Table'

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
      label: 'Paris',
      city: 'Paris',
      postalCode: '75001',
      street: '1 rue Exemple',
      departmentCode: '75',
      isLinkedToVenue: true,
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

  const renderTableWithOffer = (
    offer = baseOffer,
    options = {
      isRefactoFutureOfferEnabled: false,
      headlineOffer: null,
      isHeadlineOfferAllowedForOfferer: true,
    }
  ) => {
    const columns = getIndividualOfferColumns(
      options.isRefactoFutureOfferEnabled,
      options.headlineOffer,
      options.isHeadlineOfferAllowedForOfferer
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
            onFilterReset: function (): void {
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
    expect(screen.getByText(/Paris - 1 rue Exemple 75001/i)).toBeInTheDocument()
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
          remainingQuantity: 'unlimited',
          beginningDatetime: new Date().toISOString(),
        },
        { remainingQuantity: 2, beginningDatetime: new Date().toISOString() },
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
