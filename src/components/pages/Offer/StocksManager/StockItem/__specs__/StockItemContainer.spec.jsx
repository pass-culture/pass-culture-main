import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Provider } from 'react-redux'
import { Route, Router, Switch } from 'react-router-dom'
import configureStore from 'redux-mock-store'

import StockItemContainer, { mapStateToProps } from '../StockItemContainer'
import state from '../../../../../utils/mocks/state'
import { mapDispatchToProps } from '../StockItemContainer'

describe('mount', () => {
  it('should reset the form when click on cancel button', () => {
    // given
    const history = createBrowserHistory()
    history.push(`/offres/AE?gestion&stockAE=modification`)
    const middleWares = []
    const mockStore = configureStore(middleWares)
    const stock = { offerId: 'AE', id: 'AE' }
    const store = mockStore({
      data: {
        offers: [{ id: 'AE', venueId: 'AE' }],
        offerers: [{ id: 'AE' }],
        products: [{ id: 'AE' }],
        stocks: [stock],
        venues: [{ id: 'AE', managingOffererId: 'AE' }],
      },
    })

    const props = {
      closeInfo: jest.fn(),
      isEvent: true,
      showInfo: jest.fn(),
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

    // when
    wrapper.find("input[name='beginningTime']").simulate('change', { target: { value: '12:13' } })

    expect(wrapper.find("input[name='beginningTime']").props().value).toStrictEqual('12:13')

    // when
    const cancelButton = wrapper.find('button[type="reset"]')
    cancelButton.simulate('click')

    // then
    expect(wrapper.find("input[name='beginningTime']").props().value).toStrictEqual('')
  })

  describe('mapStateToProps', () => {
    describe('when adding stock to one offer', () => {
      it('should map correctly the state', () => {
        // given
        const ownProps = {
          location: {
            search: '?lieu=DA',
          },
          match: {
            params: { offerId: 'UU' },
          },
          query: {
            parse: () => ({}),
          },
        }

        // when
        const result = mapStateToProps(state, ownProps)
        const expected = {
          event: undefined,
          formBeginningDatetime: undefined,
          formBookingLimitDatetime: undefined,
          formEndDatetime: undefined,
          formPrice: undefined,
          hasIban: 'FR7630001007941234567890185',
          isStockReadOnly: true,
          offer: {
            bookingEmail: 'booking.email@test.com',
            dateCreated: '2019-03-07T10:39:23.560392Z',
            dateModifiedAtLastProvider: '2019-03-07T10:40:05.443621Z',
            isEvent: false,
            isThing: true,
            id: 'UU',
            idAtProviders: null,
            isActive: true,
            lastProviderId: null,
            mediationsIds: ['H4'],
            modelName: 'Offer',
            productId: 'LY',
            stocksIds: ['MU'],
            venueId: 'DA',
          },
          stockFormKey: null,
          stockIdOrNew: undefined,
          formInitialValues: {
            available: 10,
            bookingLimitDatetime: null,
            bookingRecapSent: null,
            dateModified: '2019-03-07T10:40:07.318721Z',
            dateModifiedAtLastProvider: '2019-03-07T10:40:07.318695Z',
            groupSize: 1,
            id: 'MU',
            idAtProviders: null,
            isSoftDeleted: false,
            lastProviderId: null,
            modelName: 'Stock',
            offerId: 'UU',
            offererId: 'BA',
            price: 17,
          },
          tz: 'Europe/Paris',
          venue: {
            address: null,
            bookingEmail: 'john.doe@test.com',
            city: null,
            comment: null,
            dateModifiedAtLastProvider: '2019-03-07T10:40:03.234016Z',
            departementCode: null,
            id: 'DA',
            idAtProviders: null,
            isValidated: true,
            isVirtual: true,
            lastProviderId: null,
            latitude: 48.83638,
            longitude: 2.40027,
            managingOffererId: 'BA',
            modelName: 'Venue',
            name: 'Le Sous-sol (Offre numérique)',
            postalCode: null,
            siret: null,
            thumbCount: 0,
            validationToken: null,
          },
          venueId: 'DA',
        }

        // then
        expect(result.offer).toStrictEqual(expected.offer)
      })
    })
  })

  describe('mapDispatchToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    it('should submit stock item modification', () => {
      // given
      const handleSuccess = jest.fn()
      const handleFail = jest.fn()
      const ownProps = {
        query: {
          context: jest.fn().mockReturnValue({
            method: '',
          }),
        },
        stockPatch: {
          id: '',
          stockId: '',
        },
      }
      const body = ''
      const stockId = 'stockId'

      // when
      mapDispatchToProps(dispatch, ownProps).updateStockInformations(
        stockId,
        body,
        handleSuccess,
        handleFail
      )

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: {
          apiPath: '/stocks/stockId',
          body: '',
          handleSuccess,
          handleFail,
          method: '',
        },
        type: 'REQUEST_DATA__/STOCKS/STOCKID',
      })
    })
  })
})
