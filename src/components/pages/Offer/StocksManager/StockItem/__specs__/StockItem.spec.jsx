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
import Offer from '../../ValueObjects/Offer'

describe('src | components | pages | Offer | StocksManager | StockItem', () => {
  let props

  beforeEach(() => {
    props = {
      closeInfo: jest.fn(),
      dispatch: jest.fn(),
      handleEditSuccess: jest.fn(),
      handleSetErrors: jest.fn(),
      hasIban: false,
      history: { push: jest.fn() },
      isEvent: true,
      offer: new Offer(),
      query: {
        changeToReadOnly: jest.fn(),
        context: () => ({ method: 'POST' }),
      },
      showInfo: jest.fn(),
      stockPatch: {
        id: 'DG',
      },
      updateStockInformations: jest.fn(),
      deleteStock: jest.fn(),
    }
  })

  describe('on render', () => {
    describe('when offer is an event', () => {
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
          beginningDatetime: '2020-01-20T20:00:00Z',
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          bookingsQuantity: 1,
          offerId: 'EM',
          price: 48,
          quantity: 10,
        }

        props.stockPatch = {
          id: 'G9',
          beginningDatetime: '2020-01-20T20:00:00Z',
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          offerId: 'EM',
          price: 48,
          quantity: 10,
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
          beginningDatetime: '2020-01-20T20:00:00Z',
          beginningTime: '21:00',
          bookingLimitDatetime: '2020-01-20T20:00:00Z',
          id: 'G9',
          offerId: 'EM',
          price: 48,
          quantity: 10,
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

      it('should fill the quantity input when available stock is provided', () => {
        // when
        const quantityInput = wrapper
          .find(Field)
          .find({ name: 'quantity' })
          .find('input')

        // then
        expect(quantityInput.props().value).toStrictEqual(10)
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

      describe('when the stocks are attached to an offer provided from Allociné', () => {
        it('beginning time and end time should not be alterable', () => {
          // When
          props.offer = new Offer({ lastProvider: { name: 'Allociné' } })
          props.query = { context: () => ({ readOnly: false }) }
          const stockItemWrapper = shallow(<StockItem {...props} />)
          const formWrapper = shallow(stockItemWrapper.instance().renderForm({ values: {} }))

          // Then
          const eventFields = formWrapper.find(EventFields)
          expect(eventFields.props().readOnly).toBe(true)
        })
      })

      describe('when the stocks are attached to an event offer created by the user', () => {
        it('beginning time and end time should be alterable', () => {
          // When
          props.offer = new Offer({ id: 'AE', lastProvider: null })
          props.query = { context: () => ({ readOnly: false }) }
          const stockItemWrapper = shallow(<StockItem {...props} />)
          const formWrapper = shallow(stockItemWrapper.instance().renderForm({ values: {} }))

          // Then
          const eventFields = formWrapper.find(EventFields)
          expect(eventFields.props().readOnly).toBe(false)
        })
      })
    })

    describe('when offer is a thing', () => {
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
          beginningDatetime: null,
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          bookingsQuantity: 13,
          offerId: 'EM',
          price: 12,
          quantity: 56,
        }

        props.isEvent = false
        props.stock = stock
        props.timezone = 'Europe/Paris'

        props.stockPatch = {
          id: 'G9',
          beginningDatetime: null,
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          offerId: 'EM',
          price: 12,
          quantity: 56,
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
          beginningDatetime: null,
          bookingsQuantity: 13,
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          id: 'G9',
          offerId: 'EM',
          price: 12,
          quantity: 56,
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

      it('should fill the quantity input when available stock is provided', () => {
        // when
        const quantityInput = productFieldsContainerComponent
          .find(Field)
          .find({ name: 'quantity' })
          .find('input')

        // then
        expect(quantityInput.props().value).toStrictEqual(56)
      })

      it('should fill the remaining input when remaining stock is provided', () => {
        // when
        const remainingStockInput = productFieldsContainerComponent.find('#remaining-stock')

        // then
        expect(remainingStockInput.text()).toStrictEqual('43')
      })
    })
  })

  describe('when submitting on creation for event', () => {
    let wrapper

    // given
    beforeEach(() => {
      const history = createBrowserHistory()
      history.push(`/offres/EM?gestion&lieu=CE&stock=creation`)
      const middleWares = []
      const mockStore = configureStore(middleWares)

      props.stockPatch = {
        beginningDatetime: '2020-01-27T20:00:00Z',
        offerId: 'EM',
        offererId: 'ZZ',
        price: 0,
      }

      props.isEvent = true
      props.stock = {}
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
          stocks: [],
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
    })

    it('should be able to submit with only inital values', () => {
      // given
      const submitButton = wrapper.find('button[type="submit"]')
      submitButton.simulate('click')

      // then
      expect(props.updateStockInformations).toHaveBeenCalledWith(
        undefined,
        {
          beginningDatetime: '2020-01-27T20:00:00Z',
          beginningTime: '21:00',
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          offerId: 'EM',
          offererId: 'ZZ',
          price: 0,
        },
        expect.any(Function),
        expect.any(Function)
      )
    })

    it('should not submit when beginningDatetime is missing', () => {
      // given
      const beginningDatetimeInput = wrapper
        .find(Field)
        .find({ name: 'beginningDatetime' })
        .find('input')

      beginningDatetimeInput.simulate('change', { target: { value: null } })

      const submitButton = wrapper.find('button[type="submit"]')
      submitButton.simulate('click')

      // then
      expect(props.updateStockInformations).not.toHaveBeenCalled()
    })

    it('should fill bookingLimitDatetime with beginningDatetime when bookingLimitDatetime is empty', () => {
      // given
      props.stockPatch.beginningDatetime = '2020-01-27T20:00:00Z'
      props.stockPatch.bookingLimitDatetime = null

      // when
      const submitButton = wrapper.find('button[type="submit"]')
      submitButton.simulate('click')

      // then
      expect(props.updateStockInformations).toHaveBeenCalledWith(
        undefined,
        {
          beginningDatetime: '2020-01-27T20:00:00Z',
          beginningTime: '21:00',
          bookingLimitDatetime: '2020-01-27T20:00:00Z',
          offerId: 'EM',
          offererId: 'ZZ',
          price: 0,
        },
        expect.any(Function),
        expect.any(Function)
      )
    })

    it('should update bookingLimitDatetime when submitting a beginningDatetime before bookingLimitDatetime', () => {
      // given
      props.stockPatch.beginningDatetime = '2020-04-27T20:00:00Z'

      const beginningDatetimeInput = wrapper
        .find(Field)
        .find({ name: 'beginningDatetime' })
        .find('input')

      beginningDatetimeInput.simulate('change', { target: { value: '11/03/2019' } })

      const submitButton = wrapper.find('button[type="submit"]')
      submitButton.simulate('click')

      // then
      expect(props.updateStockInformations).toHaveBeenCalledWith(
        undefined,
        {
          beginningDatetime: '2019-03-11T20:00:00.000Z',
          beginningTime: '21:00',
          bookingLimitDatetime: '2019-03-11T20:00:00.000Z',
          offerId: 'EM',
          offererId: 'ZZ',
          price: 0,
        },
        expect.any(Function),
        expect.any(Function)
      )
    })
  })

  describe('handleOnFormSubmit', () => {
    it('should set state isRequestPending to true', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleOnFormSubmit({})

      // then
      expect(wrapper.state(['isRequestPending'])).toBe(true)
    })

    it('should call handleSetErrors function', () => {
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
        price: '',
        bookingLimitDatetime: '2019-03-13T22:00:00Z',
        beginningDatetime: '2019-03-13T22:00:00Z',
        quantity: '',
      }

      // when
      wrapper.instance().handleOnFormSubmit(formValues)

      // then
      expect(props.updateStockInformations).toHaveBeenCalledWith(
        'DG',
        {
          price: 0,
          bookingLimitDatetime: '2019-03-13T22:00:00Z',
          beginningDatetime: '2019-03-13T22:00:00Z',
          quantity: null,
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

      expect(props.updateStockInformations).toHaveBeenCalledWith(
        'DG',
        {
          bookingLimitDatetime: '2019-03-13T23:00:00Z',
          beginningDatetime: '2019-03-13T23:00:00Z',
        },
        expect.any(Function),
        expect.any(Function)
      )
    })
  })

  describe('handleRequestSuccess', () => {
    it('should set state isRequestPending to false', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleRequestSuccess()

      // then
      expect(wrapper.state(['isRequestPending'])).toBe(false)
    })

    it('should change updated stock to readonly', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleRequestSuccess()

      // then
      expect(props.query.changeToReadOnly).toHaveBeenCalledWith(null, {
        id: 'DG',
        key: 'stock',
      })
    })

    it('should call handleEditSuccess function in case of edition', () => {
      // given
      const stock = {
        id: 'G9',
        beginningDatetime: '2020-01-20T20:00:00Z',
        bookingLimitDatetime: '2020-01-27T20:00:00Z',
        bookingsQuantity: 1,
        offerId: 'EM',
        price: 48,
        quantity: 10,
      }
      props.stock = stock
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleRequestSuccess()

      // then
      expect(props.handleEditSuccess).toHaveBeenCalledWith()
    })

    it('should not call handleEditSuccess function in case of creation', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleRequestSuccess()

      // then
      expect(props.handleEditSuccess).not.toHaveBeenCalledWith()
    })
  })

  describe('handleRequestFail', () => {
    it('should set state isRequestPending to false', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleRequestSuccess()

      // then
      expect(wrapper.state(['isRequestPending'])).toBe(false)
    })

    it('should change updated stock to readonly', () => {
      // given
      const wrapper = shallow(<StockItem {...props} />)

      // when
      wrapper.instance().handleRequestSuccess()

      // then
      expect(props.query.changeToReadOnly).toHaveBeenCalledWith(null, {
        id: 'DG',
        key: 'stock',
      })
    })
  })
})
