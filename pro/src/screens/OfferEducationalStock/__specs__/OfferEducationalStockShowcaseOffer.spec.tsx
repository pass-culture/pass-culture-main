import { screen } from '@testing-library/react'

import { EducationalOfferType, Mode } from 'core/OfferEducational'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'

import { defaultProps, renderOfferEducationalStock } from '../__tests-utils__'
import { IOfferEducationalStockProps } from '../OfferEducationalStock'

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
    renderOfferEducationalStock(testProps)

    screen.getByText('Date et prix')
  })

  it('should render for offer with a stock', () => {
    const offer = collectiveOfferFactory({ isPublicApi: true })
    const testProps: IOfferEducationalStockProps = {
      ...defaultProps,
      offer,
      mode: Mode.EDITION,
    }
    renderOfferEducationalStock(testProps)

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
    renderOfferEducationalStock(testProps)

    const priceInput = screen.getByLabelText('Prix global TTC')
    const placeInput = screen.getByLabelText('Nombre de places')

    expect(priceInput).not.toBeDisabled()
    expect(placeInput).not.toBeDisabled()
  })
})
