import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useParams } from 'react-router'
import { axe } from 'vitest-axe'

import { buildCollectiveStock } from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffersBookableCTA } from './CollectiveOffersBookableCTA'

const renderCollectiveOffersBookableCTA = (
  stock?: React.ComponentProps<typeof CollectiveOffersBookableCTA>['stock']
) => {
  const user = userEvent.setup()
  const props = {
    offerId: 12,
    offerLink: '/lien/vers/mon/offre/12',
    stock: stock ?? buildCollectiveStock(1, 1),
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
    const stock = buildCollectiveStock(1, 2)
    const { user } = renderCollectiveOffersBookableCTA(stock)

    const cta = screen.getByRole('link', { name: 'Modifier la date limite' })
    expect(cta).toBeVisible()

    await user.click(cta)

    expect(
      screen.getByText('Modification du stock de mon offre 12')
    ).toBeVisible()
  })

  it('should render a CTA to see the offer details otherwise', async () => {
    const stock = buildCollectiveStock(8, 9)
    const { user } = renderCollectiveOffersBookableCTA(stock)

    const cta = screen.getByRole('link', { name: "Voir l'offre" })
    expect(cta).toBeVisible()

    await user.click(cta)

    expect(screen.getByText('Detail de mon offre 12')).toBeVisible()
  })
})
