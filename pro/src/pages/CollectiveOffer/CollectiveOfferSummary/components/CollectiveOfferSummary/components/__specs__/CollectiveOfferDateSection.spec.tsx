import { screen } from '@testing-library/react'

import { getCollectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CollectiveOfferDateSection,
  CollectiveOfferDateSectionProps,
} from '../CollectiveOfferDateSection'

const renderCollectiveOfferDateSection = (
  props: CollectiveOfferDateSectionProps
) => {
  renderWithProviders(<CollectiveOfferDateSection {...props} />)
}

describe('CollectiveOfferDateSection', () => {
  it('should show the dates section if there are dates in the offer', () => {
    const offer = getCollectiveOfferTemplateFactory({
      dates: { start: '2023-10-24T09:14:00', end: '2023-10-24T09:16:00' },
    })

    renderCollectiveOfferDateSection({
      offer,
    })
    expect(screen.getByText('Date et heure')).toBeInTheDocument()
  })

  it('should not show the dates section if there are no dates in the offer', () => {
    const offer = getCollectiveOfferTemplateFactory({
      dates: undefined,
    })

    renderCollectiveOfferDateSection({
      offer,
    })
    expect(
      screen.queryByText(
        'Tout au long de l’année scolaire (l’offre est permanente)'
      )
    ).toBeInTheDocument()
  })
})
