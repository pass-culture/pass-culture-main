import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import { collectiveOfferStockFactory } from 'screens/OfferEducationalStock/__tests-utils__'
import { TOTAL_PRICE_LABEL } from 'screens/OfferEducationalStock/constants/labels'

import CollectiveOfferStockSection, {
  ICollectiveOfferStockSectionProps,
} from '../CollectiveOfferStockSection'

const renderCollectiveOfferStockSection = (
  props: ICollectiveOfferStockSectionProps
) => {
  return render(<CollectiveOfferStockSection {...props} />)
}

describe('CollectiveOfferStockSection', () => {
  it('render component', () => {
    const props = {
      stock: collectiveOfferStockFactory(),
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
