import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider, connect } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'
import { compose } from 'redux'
import { assignData } from 'redux-saga-data'

import StockItem from '../StockItem'
import mapStateToProps from '../mapStateToProps'
import { withFrenchQueryRouter } from 'components/hocs'
import { configureStore } from 'utils/store'

const dispatchMock = jest.fn()

const mockRequestDataCatch = jest.fn()
jest.mock('redux-saga-data', () => {
  const actualModule = jest.requireActual('redux-saga-data')
  return {
    ...actualModule,
    requestData: config => {
      mockRequestDataCatch(config)
      return actualModule.requestData(config)
    },
  }
})

global.fetch = url => {
  return new Response(JSON.stringify({}))
}

const StockItemContainer = compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(StockItem)

describe('src | components | pages | Offer | StocksManager | StockItem', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        closeInfo: jest.fn(),
        dispatch: dispatchMock,
        hasIban: false,
        history: { push: jest.fn() },
        isEvent: false,
        query: { context: () => ({}) },
        stockPatch: {},
        stocks: [],
      }

      // when
      const wrapper = shallow(<StockItem {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('functions', () => {
    describe('handleRequestSuccess', () => {
      it('redirect to gestion at patch success', () => {
        // given
        const initialProps = {
          closeInfo: jest.fn(),
          dispatch: jest.fn(),
          history: {},
          hasIban: false,
          isEvent: false,
          offer: {
            id: 'TY',
          },
          query: { changeToReadOnly: jest.fn(), context: () => ({}) },
          stockPatch: {
            id: 'DG',
          },
          stocks: [],
        }
        const wrapper = shallow(<StockItem {...initialProps} />)

        return new Promise((resolve, reject) => {
          // when
          wrapper.instance().handleRequestSuccess(resolve)()
        }).then(() => {
          // then
          expect(initialProps.query.changeToReadOnly).toHaveBeenCalledWith(
            null,
            {
              id: 'DG',
              key: 'stock',
            }
          )
        })
      })
    })
  })
  describe('mount', () => {
    it('reset the form when we click on cancel', done => {
      // given
      const { store } = configureStore()
      const history = createBrowserHistory()
      history.push(`/offres/AE?gestion&stockAE=modification`)
      const stock = { offerId: 'AE', id: 'AE' }
      store.dispatch(
        assignData({
          offers: [{ id: 'AE', venueId: 'AE' }],
          offerers: [{ id: 'AE' }],
          products: [{ id: 'AE' }],
          stocks: [stock],
          venues: [{ id: 'AE', managingOffererId: 'AE' }],
        })
      )
      const props = {
        isEvent: true,
        stock,
      }

      const wrapper = mount(
        <Provider store={store}>
          <Router history={history}>
            <Switch>
              <Route path="/offres/:offerId">
                <StockItemContainer {...props} />
              </Route>
            </Switch>
          </Router>
        </Provider>
      )

      setTimeout(() => {
        // then (offerer request is done, form is now available)
        wrapper.update()

        // when
        wrapper
          .find("input[name='beginningTime']")
          .simulate('change', { target: { value: '12:13' } })

        setTimeout(() => {
          // then
          wrapper.update()
          expect(
            wrapper.find("input[name='beginningTime']").props().value
          ).toEqual('12:13')

          // when
          const cancelButton = wrapper.find('button.cancel-step')
          cancelButton.simulate('click')

          // then
          expect(
            wrapper.find("input[name='beginningTime']").props().value
          ).toEqual('')

          // done
          done()
        })
      })
    })
  })
})
