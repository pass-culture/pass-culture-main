import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  MostViewedOffers,
  type MostViewedOffersProps,
} from '../components/MostViewedOffers'

const renderCumulatedViews = (props: MostViewedOffersProps) => {
  return renderWithProviders(<MostViewedOffers {...props} />)
}

const MOCKED_PROPS: MostViewedOffersProps = {
  topOffers: [
    {
      offerId: 1,
      offerName: 'offer 1',
      numberOfViews: 100,
      image: null,
      isHeadlineOffer: false,
    },
    {
      offerId: 2,
      offerName: 'offer 2',
      numberOfViews: 200,
      image: null,
      isHeadlineOffer: true,
    },
    {
      offerId: 3,
      offerName: 'offer 3',
      numberOfViews: 300,
      image: null,
      isHeadlineOffer: false,
    },
  ],
}

describe('MostViewedOffers', () => {
  it('should render top offers', () => {
    renderCumulatedViews(MOCKED_PROPS)

    expect(screen.getByText('Top offres')).toBeInTheDocument()
    MOCKED_PROPS.topOffers.forEach((topOffer) => {
      expect(screen.getByText(topOffer.offerName)).toBeInTheDocument()
      expect(
        screen.getByText(new RegExp(topOffer.numberOfViews.toString()))
      ).toBeInTheDocument()
    })
  })

  it('should render headline tag for headline offer', () => {
    const headlineOffer = {
      offerId: 4,
      offerName: 'offer 4',
      numberOfViews: 400,
      image: null,
      isHeadlineOffer: true,
    }

    renderCumulatedViews({
      ...MOCKED_PROPS,
      topOffers: [headlineOffer],
    })

    expect(screen.getByText('Offre à la une')).toBeInTheDocument()
  })
})
