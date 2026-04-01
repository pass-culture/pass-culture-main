import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { useParams } from 'react-router'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffersBookableCTA } from './CollectiveOffersBookableCTA'

function getStock(
  bookingDateDaysFromToday: number,
  startDateDaysFromToday: number
): React.ComponentProps<typeof CollectiveOffersBookableCTA>['stock'] {
  const today = new Date()
  return {
    bookingLimitDatetime: addDays(
      today,
      bookingDateDaysFromToday
    ).toISOString(),
    startDatetime: addDays(today, startDateDaysFromToday).toISOString(),
    endDatetime: addDays(today, startDateDaysFromToday + 1).toISOString(),
    numberOfTickets: 100,
  }
}

const renderCollectiveOffersBookableCTA = (
  stock?: React.ComponentProps<typeof CollectiveOffersBookableCTA>['stock']
) => {
  const user = userEvent.setup()
  const props = {
    offerId: 12,
    offerLink: '/lien/vers/mon/offre/12',
    stock: stock ?? getStock(1, 1),
  }

  const FakeOfferDetailComponent = () => {
    const { offerId } = useParams()
    return <div>Detail de mon offre {offerId}</div>
  }

  const FakeStockEditionComponent = () => {
    const { offerId } = useParams()
    return <div>Modification du stock de mon offre {offerId}</div>
  }

  return {
    ...renderWithProviders(null, {
      routes: [
        {
          path: '/',
          element: <CollectiveOffersBookableCTA {...props} />,
        },
        {
          path: '/lien/vers/mon/offre/:offerId',
          element: <FakeOfferDetailComponent />,
        },
        {
          path: '/offre/:offerId/collectif/stocks/edition',
          element: <FakeStockEditionComponent />,
        },
      ],
    }),
    user,
  }
}

describe('<CollectiveOffersBookableCTA />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOffersBookableCTA()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render a CTA to update the booking limit if offer is going to expire', async () => {
    const stock = getStock(1, 2)
    const { user } = renderCollectiveOffersBookableCTA(stock)

    const cta = screen.getByRole('link', { name: 'Modifier la date limite' })
    expect(cta).toBeVisible()

    await user.click(cta)

    expect(
      screen.getByText('Modification du stock de mon offre 12')
    ).toBeVisible()
  })

  it('should render a CTA to see the offer details otherwise', async () => {
    const stock = getStock(8, 9)
    const { user } = renderCollectiveOffersBookableCTA(stock)

    const cta = screen.getByRole('link', { name: "Voir l'offre" })
    expect(cta).toBeVisible()

    await user.click(cta)

    expect(screen.getByText('Detail de mon offre 12')).toBeVisible()
  })
})
