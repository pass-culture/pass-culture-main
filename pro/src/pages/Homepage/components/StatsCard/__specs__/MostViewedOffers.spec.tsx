import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { HomepageEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  MostViewedOffers,
  type MostViewedOffersProps,
} from '../components/MostViewedOffers'

const renderMostViewedOffers = (props: MostViewedOffersProps) =>
  renderWithProviders(<MostViewedOffers {...props} />)

const defaultProps = {
  hasActiveIndividualOffer: true,
}

const topOffers: MostViewedOffersProps['topOffers'] = [
  {
    offerId: 1,
    name: 'Infusions : 30 recettes qui réchauffent...',
    views: 30,
    image: null,
    isHeadlineOffer: true,
  },
  {
    offerId: 2,
    name: 'Chair de poule Tome 1 : la malédiction de la momie',
    views: 10,
    image: null,
    isHeadlineOffer: false,
  },
]

describe('MostViewedOffers', () => {
  it('should track clicks on top offers with their source', async () => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockReturnValue({
      logEvent: mockLogEvent,
    })

    renderMostViewedOffers({ ...defaultProps, topOffers })

    await userEvent.click(screen.getByRole('link', { name: /Infusions/ }))

    expect(mockLogEvent).toHaveBeenCalledWith(
      HomepageEvents.CLICKED_TOP_OFFER,
      {
        from: 'top_offers',
        offerId: 1,
      }
    )
  })

  it('should render the top offers in the new stats design', () => {
    renderMostViewedOffers({ ...defaultProps, topOffers })

    expect(screen.getByText('Top offres')).toBeInTheDocument()
    expect(screen.getByText(topOffers[0].name)).toBeInTheDocument()
    expect(screen.getByText('30 vues')).toBeInTheDocument()
    expect(screen.getByText(topOffers[1].name)).toBeInTheDocument()
    expect(screen.getByText('10 vues')).toBeInTheDocument()

    expect(screen.getByRole('link', { name: /Infusions/ })).toHaveAttribute(
      'href',
      '/offre/individuelle/1/visibilite'
    )
  })

  it('should render the headline tag for a headline offer', () => {
    renderMostViewedOffers({ ...defaultProps, topOffers: [topOffers[0]] })

    expect(screen.getByText('À la une')).toBeInTheDocument()
  })

  it('should render the empty state when there are no top offers', () => {
    renderMostViewedOffers({ ...defaultProps, topOffers: [] })

    expect(
      screen.getByText(
        'Vos offres n’ont pas été consultées dernièrement, il est encore temps d’augmenter votre visibilité !'
      )
    ).toBeInTheDocument()
  })

  it('should explain that an offer must be published when there is no active offer', () => {
    renderMostViewedOffers({
      ...defaultProps,
      hasActiveIndividualOffer: false,
      topOffers,
    })

    expect(
      screen.getByText(
        'Pour rendre visible vos propositions, veuillez publier ou créer au moins une offre.'
      )
    ).toBeInTheDocument()
  })
})
