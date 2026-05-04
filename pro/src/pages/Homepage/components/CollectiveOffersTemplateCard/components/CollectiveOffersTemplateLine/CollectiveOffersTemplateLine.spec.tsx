import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { useParams } from 'react-router'
import { axe } from 'vitest-axe'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1/new'
import { formatDateTimeParts } from '@/commons/utils/date'
import { buildCollectiveOfferTemplateHome } from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOffersTemplateLine } from './CollectiveOffersTemplateLine'

describe('<CollectiveOffersTemplateLine />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <CollectiveOffersTemplateLine
        offer={buildCollectiveOfferTemplateHome()}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display the right content for a published template offer with dates', () => {
    const offer = buildCollectiveOfferTemplateHome()
    renderWithProviders(<CollectiveOffersTemplateLine offer={offer} />)

    const { date: expectedStartDate } = formatDateTimeParts(
      new Date().toISOString()
    )
    const { date: expectedEndDate } = formatDateTimeParts(
      addDays(new Date(), 30).toISOString()
    )

    expect(screen.getByText(offer.name)).toBeVisible()
    expect(screen.getByRole('img')).toBeVisible()
    expect(screen.getByText('Offre vitrine')).toBeVisible()
    expect(
      screen.getByText(`Du ${expectedStartDate} au ${expectedEndDate}`)
    ).toBeVisible()
    expect(
      screen.getByRole('button', { name: 'Créer une offre réservable' })
    ).toBeVisible()
    expect(screen.getByText('publiée')).toBeVisible()
  })

  it('should display the right content for an under review template offer', () => {
    const offer = buildCollectiveOfferTemplateHome(
      CollectiveOfferDisplayedStatus.UNDER_REVIEW
    )
    renderWithProviders(<CollectiveOffersTemplateLine offer={offer} />)

    expect(screen.getByText(offer.name)).toBeVisible()
    expect(screen.getByText('en instruction')).toBeVisible()
    expect(screen.getByRole('link', { name: "Voir l'offre" })).toBeVisible()
  })

  it('should not display dates when offer has no dates', () => {
    const offer = {
      ...buildCollectiveOfferTemplateHome(),
      dates: null,
    }
    renderWithProviders(<CollectiveOffersTemplateLine offer={offer} />)

    expect(screen.getByText(offer.name)).toBeVisible()
    expect(screen.queryByText(/^Du /)).not.toBeInTheDocument()
  })

  describe('clickable behaviour', () => {
    const renderCollectiveOffersTemplateLineWithRouter = () => {
      const user = userEvent.setup()
      const offer = buildCollectiveOfferTemplateHome()

      const FakeOfferDetailComponent = () => {
        const { offerId } = useParams()
        return <div>Detail de mon offre {offerId}</div>
      }

      return {
        ...renderWithProviders(null, {
          routes: [
            {
              path: '/',
              element: <CollectiveOffersTemplateLine offer={offer} />,
            },
            {
              path: '/offre/:offerId/collectif/recapitulatif',
              element: <FakeOfferDetailComponent />,
            },
          ],
        }),
        user,
        offer,
      }
    }

    it('should have the line clickable', async () => {
      const { user, offer } = renderCollectiveOffersTemplateLineWithRouter()
      expect(screen.getByRole('img')).toBeVisible()

      const { date: start } = formatDateTimeParts(new Date().toISOString())
      const { date: end } = formatDateTimeParts(
        addDays(new Date(), 30).toISOString()
      )
      await user.click(
        screen.getByRole('link', {
          name: `Offre vitrine - ${offer.name} - Du ${start} au ${end} - publiée`,
        })
      )

      expect(
        screen.getByText(`Detail de mon offre T-${offer.id}`)
      ).toBeVisible()
    })

    it('should have the content line clickable', async () => {
      const { user, offer } = renderCollectiveOffersTemplateLineWithRouter()
      expect(screen.getByText(offer.name)).toBeVisible()

      await user.click(screen.getByText(offer.name))

      expect(
        screen.getByText(`Detail de mon offre T-${offer.id}`)
      ).toBeVisible()
    })
  })
})
