import { mount, shallow } from 'enzyme'
import React from 'react'

import StockItem from '../StockItem'
import EventFields from '../sub-components/fields/EventFields/EventFields'
import ProductFieldsContainer from '../sub-components/fields/ProductFields/ProductFieldsContainer'
import configureStore from 'redux-mock-store'
import { createBrowserHistory } from 'history'

import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'
import { Field } from 'react-final-form'
import OfferObject from '../../../OfferObject'

describe('src | components | pages | Offer | StocksManager | StockItem', () => {
  let props

  beforeEach(() => {
    props = {
      closeInfo: jest.fn(),
      dispatch: jest.fn(),
      handleSetErrors: jest.fn(),
      hasIban: false,
      history: { push: jest.fn() },
      isEvent: true,
      offer: new OfferObject(),
      query: {
        changeToReadOnly: jest.fn(),
        context: () => ({ method: 'POST' }),
      },
      showInfo: jest.fn(),
      stockPatch: {
        id: 'DG',
      },
      stocks: [],
      updateStockInformations: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<StockItem {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('renderForm', () => {
    describe('when offer is an event', () => {
      beforeEach(() => {
        props.isEvent = true
      })

      it('should render event fields', () => {
        // When
        const stockItemWrapper = shallow(<StockItem {...props} />)
        const formWrapper = shallow(stockItemWrapper.instance().renderForm({ values: {} }))

        // Then
        const eventFields = formWrapper.find(EventFields)
        expect(eventFields).toHaveLength(1)
      })

      it('should render product fields', () => {
        // When
        const stockItemWrapper = shallow(<StockItem {...props} />)
        const formWrapper = shallow(stockItemWrapper.instance().renderForm({ values: {} }))

        // Then
        const eventFields = formWrapper.find(ProductFieldsContainer)
        expect(eventFields).toHaveLength(1)
      })

      describe('when the stocks are attached to an offer provided from Allociné', () => {
        beforeEach(() => {
          props.offer = new OfferObject({ lastProvider: { name: 'Allociné' } })
          props.query = { context: () => ({ readOnly: false }) }
        })

        it('beginning time and end time should not be alterable', () => {
          // When
          const stockItemWrapper = shallow(<StockItem {...props} />)
          const formWrapper = shallow(stockItemWrapper.instance().renderForm({ values: {} }))

          // Then
          const eventFields = formWrapper.find(EventFields)
          expect(eventFields.props().readOnly).toBe(true)
        })
      })

      describe('when the stocks are attached to an event offer', () => {
        beforeEach(() => {
          props.offer = new OfferObject({ id: 'AE', lastProvider: null })
          props.query = { context: () => ({ readOnly: false }) }
        })

        it('beginning time and end time should be alterable', () => {
          // When
          const stockItemWrapper = shallow(<StockItem {...props} />)
          const formWrapper = shallow(stockItemWrapper.instance().renderForm({ values: {} }))

          // Then
          const eventFields = formWrapper.find(EventFields)
          expect(eventFields.props().readOnly).toBe(false)
        })
      })
    })

    describe('with event', () => {
      let eventFieldComponent
      let productFieldsContainerComponent
      let wrapper

      // given
      beforeEach(() => {
        const history = createBrowserHistory()
        history.push(`/offres/EM?gestion&lieu=CE`)
        const middleWares = []
        const mockStore = configureStore(middleWares)

        const stock = {
          id: 'G9',
          available: 10,
          beginningDatetime: '2020-01-20T20:00:00Z',
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          endDatetime: '2020-01-27T22:00:00Z',
          offerId: 'EM',
          price: 48,
          remainingQuantity: 9,
        }

        props.stockPatch = {
          id: 'G9',
          available: 10,
          beginningDatetime: '2020-01-20T20:00:00Z',
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          endDatetime: '2020-01-27T22:00:00Z',
          offerId: 'EM',
          price: 48,
          remainingQuantity: 9,
        }

        props.isEvent = true
        props.stock = stock
        props.timezone = 'Europe/Paris'

        const store = mockStore({
          data: {
            offers: [
              {
                id: 'EM',
                productId: 'EM',
                venueId: 'CE',
                isEvent: true,
              },
            ],
            offerers: [{ id: 'BQ', postalCode: '97300' }],
            products: [{ id: 'AE' }],
            stocks: [stock],
            venues: [{ id: 'CE', managingOffererId: 'BQ' }],
          },
        })

        wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <Switch>
                <Route path="/offres/:offerId">
                  <StockItem {...props} />
                </Route>
              </Switch>
            </Router>
          </Provider>
        )

        eventFieldComponent = wrapper.find(EventFields)
        productFieldsContainerComponent = wrapper.find(ProductFieldsContainer)
      })

      it('should display event fields and product fields informations', () => {
        // when
        const expected = {
          available: 10,
          beginningDatetime: '2020-01-20T20:00:00Z',
          beginningTime: '21:00',
          bookingLimitDatetime: '2020-01-20T20:00:00Z',
          endDatetime: '2020-01-27T22:00:00Z',
          endTime: '23:00',
          id: 'G9',
          offerId: 'EM',
          price: 48,
          remainingQuantity: 9,
        }

        // then
        expect(eventFieldComponent).toHaveLength(1)
        expect(productFieldsContainerComponent).toHaveLength(1)
        expect(eventFieldComponent.prop('values')).toStrictEqual(expected)
      })

      it('should fill the beginningTime input when beginningDatetime is updated', () => {
        // when
        const beginningTimeInput = eventFieldComponent
          .find(Field)
          .find({ name: 'beginningTime' })
          .find('input')

        // then
        expect(beginningTimeInput.props().value).toStrictEqual('21:00')
      })

      it('should fill the endDatetimeInput input when endTime is updated', () => {
        // when
        const endDatetimeInput = eventFieldComponent
          .find(Field)
          .find({ name: 'endDatetime' })
          .find('input')

        // then
        expect(endDatetimeInput.props().value).toStrictEqual('2020-01-27T22:00:00Z')
      })

      it('should fill the beginningDatetimeInput input when beginningDatetime is updated', () => {
        // when
        const beginningDatetimeInput = eventFieldComponent
          .find(Field)
          .find({ name: 'beginningDatetime' })
          .find('input')

        // then
        expect(beginningDatetimeInput.props().value).toStrictEqual('20/01/2020')
      })

      it('should fill the price input when price is provided', () => {
        // when
        const priceInput = wrapper
          .find(Field)
          .find({ name: 'price' })
          .find('input')

        // then
        expect(priceInput.props().value).toStrictEqual(48)
      })

      it('should fill the available input when available stock is provided', () => {
        // when
        const availableInput = wrapper
          .find(Field)
          .find({ name: 'available' })
          .find('input')

        // then
        expect(availableInput.props().value).toStrictEqual(10)
      })

      it('should fill the remaining input when remaining stock is provided', () => {
        // when
        const remainingStockInput = wrapper.find('#remaining-stock')

        // then
        expect(remainingStockInput.text()).toStrictEqual('9')
      })

      it('should fill the bookingLimitDatetimeInput input when booking limit date is provided', () => {
        // when
        const bookingLimitDatetimeInput = wrapper
          .find(Field)
          .find({ name: 'bookingLimitDatetime' })
          .find('input')

        // then
        expect(bookingLimitDatetimeInput.props().value).toStrictEqual('20/01/2020')
      })
    })

    describe('with product', () => {
      let eventFieldComponent
      let productFieldsContainerComponent
      let wrapper

      beforeEach(() => {
        const history = createBrowserHistory()
        history.push(`/offres/EM?gestion&lieu=CE`)
        const middleWares = []
        const mockStore = configureStore(middleWares)

        const stock = {
          id: 'G9',
          available: 56,
          beginningDatetime: null,
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          offerId: 'EM',
          price: 12,
          remainingQuantity: 31,
        }

        props.isEvent = false
        props.stock = stock
        props.timezone = 'Europe/Paris'

        props.stockPatch = {
          id: 'G9',
          available: 56,
          beginningDatetime: null,
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          offerId: 'EM',
          price: 12,
          remainingQuantity: 31,
        }

        const store = mockStore({
          data: {
            offers: [
              {
                id: 'EM',
                productId: 'EM',
                venueId: 'CE',
                isEvent: true,
              },
            ],
            offerers: [{ id: 'BQ', postalCode: '97300' }],
            products: [{ id: 'AE' }],
            stocks: [stock],
            venues: [{ id: 'CE', managingOffererId: 'BQ' }],
          },
        })

        wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <Switch>
                <Route path="/offres/:offerId">
                  <StockItem {...props} />
                </Route>
              </Switch>
            </Router>
          </Provider>
        )

        eventFieldComponent = wrapper.find(EventFields)
        productFieldsContainerComponent = wrapper.find(ProductFieldsContainer)
      })

      it('should display product fields informations', () => {
        // when
        const expected = {
          available: 56,
          beginningDatetime: null,
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          id: 'G9',
          offerId: 'EM',
          price: 12,
          remainingQuantity: 31,
        }

        // then
        expect(eventFieldComponent).toHaveLength(0)
        expect(productFieldsContainerComponent).toHaveLength(1)
        expect(productFieldsContainerComponent.prop('stock')).toStrictEqual(expected)
        expect(productFieldsContainerComponent.prop('beginningDatetime')).toBeNull()
      })

      it('should fill the  bookingLimitDatetime input when bookingLimitDatetime is updated', () => {
        // when
        const bookingLimitDatetimeInput = productFieldsContainerComponent
          .find(Field)
          .find({ name: 'bookingLimitDatetime' })
          .find('input')

        // then
        expect(bookingLimitDatetimeInput.props().value).toStrictEqual('27/01/2020')
      })

      it('should fill the price input when price is provided', () => {
        // when

        const priceInput = productFieldsContainerComponent
          .find(Field)
          .find({ name: 'price' })
          .find('input')

        // then
        expect(priceInput.props().value).toStrictEqual(12)
      })

      it('should fill the available input when available stock is provided', () => {
        // when
        const availableInput = productFieldsContainerComponent
          .find(Field)
          .find({ name: 'available' })
          .find('input')

        // then
        expect(availableInput.props().value).toStrictEqual(56)
      })

      it('should fill the remaining input when remaining stock is provided', () => {
        // when
        const remainingStockInput = productFieldsContainerComponent.find('#remaining-stock')

        // then
        expect(remainingStockInput.text()).toStrictEqual('31')
      })
    })
  })

  describe('handleOnFormSubmit()', () => {
    it('should set state isRequestPending to true', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleOnFormSubmit({})

      // then
      expect(wrapper.state(['isRequestPending'])).toBe(true)
    })

    it('should called handleSetErrors function', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleOnFormSubmit({})

      // then
      expect(props.handleSetErrors).toHaveBeenCalledWith()
    })

    it('should call updateStockInformations', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)
      const formValues = {
        available: '',
        price: '',
        bookingLimitDatetime: '2019-03-13T22:00:00Z',
        beginningDatetime: '2019-03-13T22:00:00Z',
      }

      // when
      wrapper.instance().handleOnFormSubmit(formValues)

      // then
      expect(props.updateStockInformations).toHaveBeenCalledWith(
        'DG',
        {
          available: null,
          price: 0,
          bookingLimitDatetime: '2019-03-13T22:00:00Z',
          beginningDatetime: '2019-03-13T22:00:00Z',
        },
        expect.any(Function),
        expect.any(Function)
      )
    })

    it('should call updateStockInformations when offer is Event and booking limit date time is not provided', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)
      const formValues = {
        bookingLimitDatetime: '',
        beginningDatetime: '2019-03-13T23:00:00Z',
      }

      // when
      wrapper.instance().handleOnFormSubmit(formValues)

      // then

      expect(props.updateStockInformations).toHaveBeenCalledWith('DG',
          {
            bookingLimitDatetime: '2019-03-13T22:00:00Z',
            beginningDatetime: '2019-03-13T22:00:00Z',
          },
          expect.any(Function),
          expect.any(Function))
    })
  })

  describe('handleRequestSuccess()', () => {
    it('redirect to gestion at patch success', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleRequestSuccess(jest.fn())

      // then
      expect(props.query.changeToReadOnly).toHaveBeenCalledWith(null, {
        id: 'DG',
        key: 'stock',
      })
    })
  })
})
