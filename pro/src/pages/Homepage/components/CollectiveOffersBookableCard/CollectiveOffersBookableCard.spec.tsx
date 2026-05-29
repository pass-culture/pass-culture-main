import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import { buildCollectiveOfferHome } from '@/commons/utils/factories/adageFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { OffersCardVariant } from '../types'
import { CollectiveOffersBookableCard } from './CollectiveOffersBookableCard'
import type { CollectiveOffersBookableLineProps } from './components/CollectiveOffersBookableLine/CollectiveOffersBookableLine'

vi.mock(
  './components/CollectiveOffersBookableLine/CollectiveOffersBookableLine',
  () => ({
    CollectiveOffersBookableLine: ({
      offer,
    }: CollectiveOffersBookableLineProps) => (
      <div data-testid="collective-offer-line">Line for offer {offer.id}</div>
    ),
  })
)

const mockLogEvent = vi.fn()

describe('<CollectiveOffersBookableCard />', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <CollectiveOffersBookableCard offers={[buildCollectiveOfferHome()]} />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render one CollectiveOffersBookableLine per offer given', () => {
    const collectiveOfferHome = buildCollectiveOfferHome()
    renderWithProviders(
      <CollectiveOffersBookableCard
        offers={[
          { ...collectiveOfferHome, id: 1 },
          { ...collectiveOfferHome, id: 2 },
          { ...collectiveOfferHome, id: 3 },
        ]}
      />
    )

    const allOfferLines = screen.getAllByTestId('collective-offer-line')
    expect(allOfferLines.length).toBe(3)
    allOfferLines.forEach((line, idx) => {
      expect(line).toHaveTextContent(`Line for offer ${idx + 1}`)
    })
  })

  it('should have a CTA that sends to collective offer list', async () => {
    const user = userEvent.setup()
    const collectiveOfferHome = buildCollectiveOfferHome(1)

    renderWithProviders(null, {
      routes: [
        {
          path: '/',
          element: (
            <CollectiveOffersBookableCard offers={[collectiveOfferHome]} />
          ),
        },
        {
          path: '/offres/collectives',
          element: <div>Liste de toutes les offres réservables</div>,
        },
      ],
    })

    const allOffersBtn = screen.getByRole('link', {
      name: 'Voir toutes les offres',
    })
    expect(allOffersBtn).toBeVisible()
    await user.click(allOffersBtn)

    expect(
      screen.getByText('Liste de toutes les offres réservables')
    ).toBeVisible()
  })

  it('should log event on press CTA that sends to collective offer list', async () => {
    const user = userEvent.setup()
    const collectiveOfferHome = buildCollectiveOfferHome(1)

    renderWithProviders(
      <CollectiveOffersBookableCard offers={[collectiveOfferHome]} />
    )

    const allOffersBtn = screen.getByRole('link', {
      name: 'Voir toutes les offres',
    })
    expect(allOffersBtn).toBeVisible()
    await user.click(allOffersBtn)

    expect(mockLogEvent).toHaveBeenCalledWith(
      HomepageEvents.CLICKED_SEE_ALL_OFFERS,
      {
        offersVariant: OffersCardVariant.BOOKABLE,
        hasOffersDisplayed: true,
      }
    )
  })
})
