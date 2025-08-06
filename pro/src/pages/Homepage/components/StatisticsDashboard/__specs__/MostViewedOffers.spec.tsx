import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  MostViewedOffers,
  MostViewedOffersProps,
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
      isHeadlineOffer: false,
    },
    {
      offerId: 2,
      offerName: 'offer 2',
      numberOfViews: 200,
      isHeadlineOffer: true,
    },
    {
      offerId: 3,
      offerName: 'offer 3',
      numberOfViews: 300,
      isHeadlineOffer: false,
    },
  ],
  last30daysViews: 1000,
}

describe('MostViewedOffers', () => {
  it('should render top offers and last 30 days views count', () => {
    renderCumulatedViews(MOCKED_PROPS)

    MOCKED_PROPS.topOffers.forEach((topOffer, index) => {
      expect(screen.getByText(`#${index + 1}`)).toBeInTheDocument()
      expect(screen.getByText(topOffer.offerName)).toBeInTheDocument()
      expect(
        screen.getByText(new RegExp(topOffer.numberOfViews.toString()))
      ).toBeInTheDocument()
    })
    expect(screen.getByText(/1 000 fois/)).toBeInTheDocument()
  })

  it('should render headline tag for headline offer', () => {
    const headlineOffer = {
      offerId: 4,
      offerName: 'offer 4',
      numberOfViews: 400,
      isHeadlineOffer: true,
    }

    renderCumulatedViews({
      ...MOCKED_PROPS,
      topOffers: [headlineOffer],
    })

    expect(screen.getByText('Offre à la une')).toBeInTheDocument()
  })
})
