import { render, screen } from '@testing-library/react'
import React from 'react'

import { TOTAL_PRICE_LABEL } from 'screens/OfferEducationalStock/constants/labels'
import { collectiveStockFactory } from 'utils/collectiveApiFactories'

import CollectiveOfferStockSection, {
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
      stock: collectiveStockFactory(),
    }
    renderCollectiveOfferStockSection(props)

    expect(screen.getByText('Date :')).toBeInTheDocument()
    expect(screen.getByText('Horaire :')).toBeInTheDocument()
    expect(screen.getByText('Nombre de places :')).toBeInTheDocument()
    expect(screen.getByText(`${TOTAL_PRICE_LABEL} :`)).toBeInTheDocument()
    expect(screen.getByText('Date limite de réservation :')).toBeInTheDocument()
    expect(screen.getByText('Détails :')).toBeInTheDocument()
  })
})
