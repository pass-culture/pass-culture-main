import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { useParams } from 'react-router'
import { axe } from 'vitest-axe'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1/new'
import { formatDateTimeParts } from '@/commons/utils/date'
import { buildCollectiveOfferHome } from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffersBookableLine } from './CollectiveOffersBookableLine'

describe('<CollectiveOffersBookableLine />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <CollectiveOffersBookableLine offer={buildCollectiveOfferHome()} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the right content for non expiring offers', () => {
    const collectiveOfferHome = buildCollectiveOfferHome(
      10,
      11,
      CollectiveOfferDisplayedStatus.BOOKED
    )
    renderWithProviders(
      <CollectiveOffersBookableLine offer={collectiveOfferHome} />
    )

    const { date: expectedDispalyedDate } = formatDateTimeParts(
      addDays(new Date(), 11).toISOString()
    )
    expect(screen.getByText(collectiveOfferHome.name)).toBeVisible()
    expect(screen.getByRole('img')).toBeVisible()
    expect(
      screen.getByText(`Prévu le ${expectedDispalyedDate} - 100 participants`)
    ).toBeVisible()
    expect(screen.getByRole('link', { name: "Voir l'offre" })).toBeVisible()
    expect(screen.getByText('réservée')).toBeVisible()
    expect(screen.getByText('Dans 11 jours')).toBeVisible()
  })

  it('should display the right content for expiring offers', () => {
    const collectiveOfferHome = buildCollectiveOfferHome(
      3,
      11,
      CollectiveOfferDisplayedStatus.PUBLISHED
    )
    renderWithProviders(
      <CollectiveOffersBookableLine offer={collectiveOfferHome} />
    )

    const { date: expectedDispalyedDate } = formatDateTimeParts(
      addDays(new Date(), 11).toISOString()
    )
    expect(screen.getByText(collectiveOfferHome.name)).toBeVisible()
    expect(screen.getByRole('img')).toBeVisible()
    expect(
      screen.getByText(`Prévu le ${expectedDispalyedDate} - 100 participants`)
    ).toBeVisible()
    expect(
      screen.getByRole('link', { name: 'Modifier la date limite' })
    ).toBeVisible()
    expect(screen.getByText('publiée')).toBeVisible()
    expect(screen.getByText('Expire dans 3 jours')).toBeVisible()
  })

  describe('clickable behaviour', () => {
    const renderCollectiveOffersBookableLineWithRouter = () => {
      const user = userEvent.setup()
      const collectiveOfferHome = buildCollectiveOfferHome(1)

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
              element: (
                <CollectiveOffersBookableLine offer={collectiveOfferHome} />
              ),
            },
            {
              path: '/offre/:offerId/collectif/recapitulatif',
              element: <FakeOfferDetailComponent />,
            },
            {
              path: '/offre/:offerId/collectif/stocks/edition',
              element: <FakeStockEditionComponent />,
            },
          ],
        }),
        user,
        collectiveOfferHome,
      }
    }

    it('should have the thumbnail line clickable', async () => {
      const { user, collectiveOfferHome } =
        renderCollectiveOffersBookableLineWithRouter()
      expect(screen.getByText(collectiveOfferHome.name)).toBeVisible()

      await user.click(screen.getByRole('img'))

      expect(
        screen.getByText(`Detail de mon offre ${collectiveOfferHome.id}`)
      ).toBeVisible()
    })

    it('should have the content line clickable', async () => {
      const { user, collectiveOfferHome } =
        renderCollectiveOffersBookableLineWithRouter()
      expect(screen.getByText(collectiveOfferHome.name)).toBeVisible()

      await user.click(screen.getByText(collectiveOfferHome.name))

      expect(
        screen.getByText(`Detail de mon offre ${collectiveOfferHome.id}`)
      ).toBeVisible()
    })

    it('should have the displayedStatus line clickable', async () => {
      const { user, collectiveOfferHome } =
        renderCollectiveOffersBookableLineWithRouter()
      expect(screen.getByText(collectiveOfferHome.name)).toBeVisible()

      await user.click(screen.getByText('publiée'))

      expect(
        screen.getByText(`Detail de mon offre ${collectiveOfferHome.id}`)
      ).toBeVisible()
    })

    it('the CTA should still redirect to its own link', async () => {
      const { user, collectiveOfferHome } =
        renderCollectiveOffersBookableLineWithRouter()
      expect(screen.getByText(collectiveOfferHome.name)).toBeVisible()

      await user.click(
        screen.getByRole('link', { name: 'Modifier la date limite' })
      )

      expect(
        screen.getByText(
          `Modification du stock de mon offre ${collectiveOfferHome.id}`
        )
      ).toBeVisible()
    })
  })
})
