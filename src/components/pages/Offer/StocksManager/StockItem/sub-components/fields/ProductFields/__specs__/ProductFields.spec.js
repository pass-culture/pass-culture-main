import { shallow } from 'enzyme'

import ProductFields from '../ProductFields'
import React from 'react'
import HiddenField from '../../../../../../../../layout/form/fields/HiddenField'
import NumberField from '../../../../../../../../layout/form/fields/NumberField'
import DateField from '../../../../../../../../layout/form/fields/DateField'

describe('src | components | pages | Offer | StocksManager | StockItem | sub-components | fields | ProductFields', () => {
  let props

  beforeEach(() => {
    props = {
      assignModalConfig: jest.fn(),
      beginningDatetime: '2019-01-01',
      closeInfo: jest.fn(),
      hasIban: false,
      isEvent: false,
      readOnly: false,
      showInfo: jest.fn(),
      stock: {
        available: 2,
        remainingQuantity: 1,
      },
      timezone: 'UTC',
      venue: {},
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<ProductFields {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render two HiddenField components with the right props for offerId and venueId', () => {
      // when
      const wrapper = shallow(<ProductFields {...props} />)

      // then
      const hiddenFields = wrapper.find(HiddenField)
      expect(hiddenFields).toHaveLength(2)
      expect(hiddenFields.at(0).prop('name')).toBe('offerId')
      expect(hiddenFields.at(0).prop('type')).toBe('hidden')
      expect(hiddenFields.at(1).prop('name')).toBe('venueId')
      expect(hiddenFields.at(1).prop('type')).toBe('hidden')
    })

    it('should render a NumberField component for price input with the right props', () => {
      // when
      const wrapper = shallow(<ProductFields {...props} />)

      // then
      const numberField = wrapper.find(NumberField).first()
      expect(numberField).toHaveLength(1)
      expect(numberField.prop('format')).toStrictEqual(expect.any(Function))
      expect(numberField.prop('name')).toBe('price')
      expect(numberField.prop('onBlur')).toStrictEqual(expect.any(Function))
      expect(numberField.prop('placeholder')).toBe('Gratuit')
      expect(numberField.prop('readOnly')).toBe(false)
      expect(numberField.prop('title')).toBe('Prix')
    })

    it('should render a DateField component for booking limit date time', () => {
      // when
      const wrapper = shallow(<ProductFields {...props} />)

      // then
      const dateField = wrapper.find(DateField)
      expect(dateField).toHaveLength(1)
      expect(dateField.prop('maxDate')).toStrictEqual(undefined)
      expect(dateField.prop('name')).toBe('bookingLimitDatetime')
      expect(dateField.prop('placeholder')).toBe('Laissez vide si pas de limite')
      expect(dateField.prop('readOnly')).toBe(false)
      expect(dateField.prop('renderValue')).toStrictEqual(expect.any(Function))
      expect(dateField.prop('timezone')).toBe('UTC')
    })

    it('should render a NumberField component for number of stocks/seats with the right props', () => {
      // when
      const wrapper = shallow(<ProductFields {...props} />)

      // then
      const numberField = wrapper.find(NumberField).at(1)
      expect(numberField).toHaveLength(1)
      expect(numberField.prop('format')).toStrictEqual(expect.any(Function))
      expect(numberField.prop('name')).toBe('available')
      expect(numberField.prop('placeholder')).toBe('Illimité')
      expect(numberField.prop('readOnly')).toBe(false)
      expect(numberField.prop('renderValue')).toStrictEqual(expect.any(Function))
      expect(numberField.prop('title')).toBe('Stock[ou] Place[s] affecté[es]')
    })

    it('should display remaining stock when given', () => {
      // when
      const wrapper = shallow(<ProductFields {...props} />)

      // then
      const remainingStockElement = wrapper.find('#remaining-stock')
      expect(remainingStockElement).toHaveLength(1)
      expect(remainingStockElement.text()).toBe('1')
    })
  })

  describe('when componentWillUnmount', () => {
    it('should close popup info', () => {
      // given
      const wrapper = shallow(<ProductFields {...props} />)

      // when
      wrapper.unmount()

      // then
      expect(props.closeInfo).toHaveBeenCalledWith()
    })
  })

  describe('functions', () => {
    describe('handleOnClick', () => {
      it('should reset modal config and close popup info', () => {
        // given
        const wrapper = shallow(<ProductFields {...props} />)

        // when
        wrapper.instance().handleOnClick()

        // then
        expect(props.assignModalConfig).toHaveBeenCalledWith(null)
        expect(props.closeInfo).toHaveBeenCalledWith()
      })
    })

    describe('handleOnPriceBlur', () => {
      let event

      beforeEach(() => {
        event = {
          target: {
            focus: jest.fn(),
            value: 12,
          },
        }
      })

      it('should focus on element when price has been provided', () => {
        // given
        const wrapper = shallow(<ProductFields {...props} />)

        // when
        wrapper.instance().handleOnPriceBlur(event)

        // then
        expect(event.target.focus).toHaveBeenCalledWith()
      })

      it('should assign config to modal when price has been provided', () => {
        // given
        const wrapper = shallow(<ProductFields {...props} />)

        // when
        wrapper.instance().handleOnPriceBlur(event)

        // then
        expect(props.assignModalConfig).toHaveBeenCalledWith('modal-in-modal')
      })

      it('should display info in a modal when price has been provided', () => {
        // given
        const expected = (
          <React.Fragment>
            <div className="mb24 has-text-left">
              {'Vous avez saisi une offre payante. Pensez à demander à '}
              {'l’administrateur financier nommé pour votre structure de renseigner '}
              {'son IBAN. Sans IBAN, les réservations de vos offres éligibles ne vous '}
              {'seront pas remboursées.'}
            </div>
            <div className="has-text-right">
              <button
                className="button is-primary"
                onClick={expect.any(Function)}
                type="button"
              >
                {'J’ai compris'}
              </button>
            </div>
          </React.Fragment>
        )
        const wrapper = shallow(<ProductFields {...props} />)

        // when
        wrapper.instance().handleOnPriceBlur(event)

        // then
        expect(props.showInfo).toHaveBeenCalledWith(expected)
      })
    })
  })
})
