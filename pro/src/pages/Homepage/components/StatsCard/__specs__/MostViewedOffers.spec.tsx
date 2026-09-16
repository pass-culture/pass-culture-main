import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  MostViewedOffers,
  type MostViewedOffersProps,
} from '../components/MostViewedOffers'

const renderMostViewedOffers = (props: MostViewedOffersProps) =>
  renderWithProviders(<MostViewedOffers {...props} />)

const topOffers: MostViewedOffersProps['topOffers'] = [
  {
    offerId: 1,
    offerName: 'Infusions : 30 recettes qui réchauffent...',
    numberOfViews: 30,
    image: null,
    isHeadlineOffer: true,
  },
  {
    offerId: 2,
    offerName: 'Chair de poule Tome 1 : la malédiction de la momie',
    numberOfViews: 10,
    image: null,
    isHeadlineOffer: false,
  },
]

describe('MostViewedOffers', () => {
  it('should render the top offers in the new stats design', () => {
    renderMostViewedOffers({ topOffers })

    expect(
      screen.getByRole('heading', { name: 'Top offres' })
    ).toBeInTheDocument()
    expect(screen.getByText(topOffers[0].offerName)).toBeInTheDocument()
    expect(screen.getByText('30 vues')).toBeInTheDocument()
    expect(screen.getByText(topOffers[1].offerName)).toBeInTheDocument()
    expect(screen.getByText('10 vues')).toBeInTheDocument()
  })

  it('should render the headline tag for a headline offer', () => {
    renderMostViewedOffers({ topOffers: [topOffers[0]] })

    expect(screen.getByText('À la une')).toBeInTheDocument()
  })
})
