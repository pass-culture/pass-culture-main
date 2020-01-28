import { mount, shallow } from 'enzyme'
import React from 'react'

import StockItem from '../StockItem'
import EventFields from '../sub-components/fields/EventFields/EventFields'
import ProductFieldsContainer from '../sub-components/fields/ProductFields/ProductFieldsContainer'
import configureStore from 'redux-mock-store'
import { createBrowserHistory } from 'history'

import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'
import StockItemContainer from '../StockItemContainer'
import { Field } from 'react-final-form'

describe('src | components | pages | Offer | StocksManager | StockItem', () => {
  let props

  beforeEach(() => {
    props = {
      closeInfo: jest.fn(),
      dispatch: jest.fn(),
      handleSetErrors: jest.fn(),
      hasIban: false,
      history: { push: jest.fn() },
      isEvent: false,
      offer: {
        id: 'TY',
      },
      query: {
        changeToReadOnly: jest.fn(),
        context: () => ({ method: 'POST' }),
      },
      showInfo: jest.fn(),
      stockPatch: {
        id: 'DG',
      },
      stocks: [],
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<StockItem {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('renderForm', () => {
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
          remainingQuantity: 9
        }

        props.isEvent = true
        props.stock = stock

        const store = mockStore({
          data: {
            offers: [
              {
                id: 'EM',
                productId: 'EM',
                venueId: 'CE',
                isEvent: true
              }
            ],
            offerers: [
              { id: 'BQ', postalCode: '97300' }
            ],
            products: [{ id: 'AE' }],
            stocks: [stock],
            venues: [{ id: 'CE', managingOffererId:'BQ' }],
          },
        })

        wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <Switch>
                <Route path='/offres/:offerId'>
                  <StockItemContainer {...props} />
                </Route>
              </Switch>
            </Router>
          </Provider>
        )

        eventFieldComponent = wrapper.find(EventFields)
        productFieldsContainerComponent = wrapper.find(ProductFieldsContainer)
      })

        it('should display event fields informations', () => {
          // when
          const expected = {
            "available": 10,
            "beginningDatetime": "2020-01-20T20:00:00Z",
            "beginningTime": "21:00",
            "bookingLimitDatetime": "2020-01-20T20:00:00Z",
            "endDatetime": "2020-01-27T22:00:00Z",
            "endTime": "23:00",
            "id": "G9",
            "offerId": "EM",
            "offererId": "BQ",
            "price": 48
          }

          // then
          expect(eventFieldComponent).toHaveLength(1)
          expect(productFieldsContainerComponent).toHaveLength(1)
          expect(eventFieldComponent.prop('values')).toStrictEqual(expected)

          const beginningTimeInput = eventFieldComponent
            .find(Field)
            .find({ name: 'beginningTime' })
            .find('input')

          const endDatetimeInput = eventFieldComponent
            .find(Field)
            .find({ name: 'endDatetime' })
            .find('input')

          const beginningDatetimeInput = eventFieldComponent
            .find(Field)
            .find({ name: 'beginningDatetime' })
            .find('input')

          expect(beginningDatetimeInput.props().value).toStrictEqual('20/01/2020')
          expect(beginningTimeInput.props().value).toStrictEqual('21:00')
          expect(endDatetimeInput.props().value).toStrictEqual('2020-01-27T22:00:00Z')
        })

        it('should display product fields informations', () => {
          // then
          const priceInput = wrapper
            .find(Field)
            .find({ name: 'price' })
            .find('input')

          const availableInput = wrapper
            .find(Field)
            .find({ name: 'available' })
            .find('input')

          const remainingStockInput = wrapper.find('#remaining-stock')

          const bookingLimitDatetimeInput = wrapper
            .find(Field)
            .find({ name: 'bookingLimitDatetime' })
            .find('input')

          expect(priceInput.props().value).toStrictEqual(48)
          expect(availableInput.props().value).toStrictEqual(10)
          expect(bookingLimitDatetimeInput.props().value).toStrictEqual('20/01/2020')
          expect(remainingStockInput.text()).toStrictEqual('9')
        })
      })

    describe('with product', () => {
      it('should display product fields informations', () => {
        // when
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
          remainingQuantity: 31
        }

        props.isEvent = false
        props.stock = stock

        const store = mockStore({
          data: {
            offers: [
              {
                id: 'EM',
                productId: 'EM',
                venueId: 'CE',
                isEvent: true
              }
            ],
            offerers: [
              { id: 'BQ', postalCode: '97300' }
            ],
            products: [{ id: 'AE' }],
            stocks: [stock],
            venues: [{ id: 'CE', managingOffererId:'BQ' }],
          },
        })

        const wrapper = mount(
          <Provider store={store}>
            <Router history={history}>
              <Switch>
                <Route path='/offres/:offerId'>
                  <StockItemContainer {...props} />
                </Route>
              </Switch>
            </Router>
          </Provider>
        )

        const eventFieldComponent = wrapper.find(EventFields)
        const productFieldsContainerComponent = wrapper.find(ProductFieldsContainer)

        // then
        const bookingLimitDatetimeInput = productFieldsContainerComponent
          .find(Field)
          .find({ name: 'bookingLimitDatetime' })
          .find('input')

        const priceInput = productFieldsContainerComponent
          .find(Field)
          .find({ name: 'price' })
          .find('input')

        const availableInput = productFieldsContainerComponent
          .find(Field)
          .find({ name: 'available' })
          .find('input')

        const remainingStockInput = productFieldsContainerComponent.find('#remaining-stock')

        expect(eventFieldComponent).toHaveLength(0)
        expect(productFieldsContainerComponent).toHaveLength(1)

        expect(priceInput.props().value).toStrictEqual(12)
        expect(availableInput.props().value).toStrictEqual(56)
        expect(remainingStockInput.text()).toStrictEqual('31')
        expect(bookingLimitDatetimeInput.props().value).toStrictEqual('27/01/2020')
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

    it('should dispatch request data', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)
      const formValues = {
        available: '',
        price: '',
      }

      // when
      wrapper.instance().handleOnFormSubmit(formValues)

      // then
      const result = {
        config: {
          apiPath: '/stocks/DG',
          body: {
            available: null,
            price: 0,
          },
          handleFail: expect.any(Function),
          handleSuccess: expect.any(Function),
          method: 'POST',
        },
        type: 'REQUEST_DATA_POST_/STOCKS/DG',
      }
      expect(props.dispatch).toHaveBeenCalledWith(result)
    })
  })

  describe('handleRequestSuccess()', () => {
    it('redirect to gestion at patch success', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleRequestSuccess(jest.fn())()

      // then
      expect(props.query.changeToReadOnly).toHaveBeenCalledWith(null, {
        id: 'DG',
        key: 'stock',
      })
    })
  })
})
