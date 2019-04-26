import { createBrowserHistory } from 'history'
import React from 'react'
import { mount, shallow } from 'enzyme'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { Route, Router } from 'react-router-dom'

import { Field } from 'pass-culture-shared'

import ProductFields from '../ProductFields'

import mockedState from './mockedState'
const middlewares = []
const mockStore = configureStore(middlewares)
const dispatchMock = jest.fn()
const closeInfoMock = jest.fn()
const showInfoMock = jest.fn()

describe('src | components | pages | Offer | StockItem | ProductFields', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        closeInfo: jest.fn(),
        dispatch: jest.fn(),
        parseFormChild: jest.fn(),
        showInfo: jest.fn(),
      }

      // when
      const wrapper = shallow(<ProductFields {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('functions', () => {
    describe.skip('handleOfferSuccessData', () => {
      it('should push correct url to history to permit to patch form', () => {
        // given
        const initialState = {}

        const historyMock = { push: jest.fn() }
        const initialProps = {
          closeInfo: closeInfoMock,
          dispatch: dispatchMock,
          history: historyMock,
          offer: {
            id: 'TY',
          },
          parseFormChild: jest.fn(),
          showInfo: showInfoMock,
          formInitialValues: {
            id: 'DG',
          },
          store: mockStore(initialState),
        }

        // when
        const wrapper = shallow(<ProductFields {...initialProps} />)
        const expected = '/offres/TY?gestion&date=K9&stock=DG'

        // then
        expect(wrapper.state()).toEqual('expected')
        expect(historyMock.push).toHaveBeenCalledWith(expected)
      })
    })
  })

  describe.skip('render', () => {
    describe('Quantity Field', () => {
      describe('With editedStockId', () => {
        // security error
        it('should update field with good params', () => {
          // given
          const initialState = mockedState
          const store = mockStore(initialState)
          const history = createBrowserHistory()

          const initialProps = {
            closeInfo: jest.fn(),
            history,
            isStockReadOnly: false,
            parseFormChild: jest.fn(),
            showInfo: jest.fn(),
            formInitialValues: {
              bookingLimitDatetime: null,
              eventOccurrenceId: null,
              offerId: 'UU',
              offererId: 'BA',
              id: 'MU',
              available: 10,
              bookingRecapSent: null,
              dateModified: '2019-03-07T10:40:07.318721Z',
              dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
              groupSize: 1,
              idAtProviders: null,
              isSoftDeleted: false,
              lastProviderId: null,
              modelName: 'Stock',
              price: 17,
            },
          }
          history.push('/offres/NE')

          // when
          const wrapper = mount(
            <Provider store={store}>
              <Router history={history}>
                <Route path="/test">
                  <ProductFields {...initialProps} />
                </Route>
              </Router>
            </Provider>
          )
          history.push('/offres/NE?gestion&stock=MU')

          const field = wrapper.find(Field)
          // then
          expect(field).toHaveLength(5)
        })
      })
    })
  })
})
