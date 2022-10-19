import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import CollectiveOfferStockSection, {
  ICollectiveOfferStockSectionProps,
} from '../CollectiveOfferStockSection'

const renderCollectiveOfferStockSection = (
  props: ICollectiveOfferStockSectionProps
) => {
  return render(<CollectiveOfferStockSection {...props} />)
}

describe('CollectiveOfferStockSection', () => {
  let props: ICollectiveOfferStockSectionProps
  beforeEach(() => {
    props = {
      stock: {
        beginningDatetime: '2022-10-10T13:51:29.098191Z',
        bookingLimitDatetime: '2001-03-01T13:51:29.098191Z',
        educationalPriceDetail: null,
        id: 'STOCK_ID',
        isBooked: true,
        isCancellable: false,
        numberOfTickets: 10,
        price: 200,
      },
      venueDepartmentCode: '75',
    }
  })

  it('render component', () => {
    renderCollectiveOfferStockSection(props)

    expect(screen.getByText('Date :')).toBeInTheDocument()
    expect(screen.getByText('Horaire :')).toBeInTheDocument()
    expect(screen.getByText('Nombre de places :')).toBeInTheDocument()
    expect(screen.getByText('Prix total :')).toBeInTheDocument()
    expect(screen.getByText('Date limite de réservation :')).toBeInTheDocument()
    expect(screen.getByText('Détails :')).toBeInTheDocument()
  })
})
