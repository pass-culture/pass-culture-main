import { screen } from '@testing-library/react'
import React from 'react'

import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
} from 'core/OfferEducational'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducationalStock, {
  IOfferEducationalStockProps,
} from '../OfferEducationalStock'

const defaultProps: IOfferEducationalStockProps = {
  initialValues: DEFAULT_EAC_STOCK_FORM_VALUES,
  offer: collectiveOfferFactory({}),
  onSubmit: jest.fn(),
  mode: Mode.CREATION,
}

describe('screens | OfferEducationalStock : showcase offer', () => {
  it('should render for offer with a stock', () => {
    const offer = collectiveOfferFactory()
    const testProps: IOfferEducationalStockProps = {
      ...defaultProps,
      offer,
      initialValues: {
        eventDate: new Date('2022-02-10T00:00:00.000Z'),
        eventTime: new Date('2022-02-10T00:00:00.000Z'),
        bookingLimitDatetime: new Date('2022-02-10'),
        numberOfPlaces: 10,
        totalPrice: 100,
        priceDetail: 'Détail du prix',
        educationalOfferType: EducationalOfferType.CLASSIC,
      },
      mode: Mode.EDITION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    screen.getByText('Date et prix')
  })

  it('should render for offer with a stock', () => {
    const offer = collectiveOfferFactory({ isPublicApi: true })
    const testProps: IOfferEducationalStockProps = {
      ...defaultProps,
      offer,
      mode: Mode.EDITION,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    expect(
      screen.getByText('Offre importée automatiquement')
    ).toBeInTheDocument()
  })

  it('should not disable price and place when offer status is reimbursment', () => {
    jest.useFakeTimers().setSystemTime(new Date('2021-10-16T12:00:00Z'))
    const offer = collectiveOfferFactory({ isPublicApi: false })
    const testProps: IOfferEducationalStockProps = {
      ...defaultProps,
      offer,
      mode: Mode.READ_ONLY,
    }
    renderWithProviders(<OfferEducationalStock {...testProps} />)

    const priceInput = screen.getByLabelText('Prix global TTC')
    const placeInput = screen.getByLabelText('Nombre de places')

    expect(priceInput).not.toBeDisabled()
    expect(placeInput).not.toBeDisabled()
  })
})
