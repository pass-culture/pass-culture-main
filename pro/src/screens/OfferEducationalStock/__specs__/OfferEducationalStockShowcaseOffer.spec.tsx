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
})
