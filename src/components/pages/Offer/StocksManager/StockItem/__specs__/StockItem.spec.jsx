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
      describe('when dateTime is the same day than booking limit date time', () => {
        it('should display event fields with ', () => {
          // given
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

          // when
          const eventFieldComponent = wrapper.find(EventFields)
          const ProductFieldsContainerComponent = wrapper.find(ProductFieldsContainer)

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
          expect(ProductFieldsContainerComponent).toHaveLength(1)
          expect(eventFieldComponent.prop('values')).toStrictEqual(expected)

        })
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
