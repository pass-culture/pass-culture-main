import { render, screen } from '@testing-library/react'

import { getCollectiveOfferCollectiveStockFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { TOTAL_PRICE_LABEL } from '@/pages/CollectiveOffer/CollectiveOfferStock/components/OfferEducationalStock/constants/labels'

import {
  CollectiveOfferStockSection,
  CollectiveOfferStockSectionProps,
} from '../CollectiveOfferStockSection'

const renderCollectiveOfferStockSection = (
  props: CollectiveOfferStockSectionProps
) => {
  return render(<CollectiveOfferStockSection {...props} />)
}

describe('CollectiveOfferStockSection', () => {
  it('render component', () => {
    const props = {
      stock: getCollectiveOfferCollectiveStockFactory(),
    }
    renderCollectiveOfferStockSection(props)

    expect(screen.getByText('Date de début :')).toBeInTheDocument()
    expect(screen.getByText('Date de fin :')).toBeInTheDocument()
    expect(screen.getByText('Horaire :')).toBeInTheDocument()
    expect(screen.getByText('Nombre de participants :')).toBeInTheDocument()
    expect(screen.getByText(`${TOTAL_PRICE_LABEL} :`)).toBeInTheDocument()
    expect(screen.getByText('Informations sur le prix :')).toBeInTheDocument()
    expect(screen.getByText('Date limite de réservation :')).toBeInTheDocument()
  })
})
