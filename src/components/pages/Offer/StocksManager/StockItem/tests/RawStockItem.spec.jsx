import { shallow } from 'enzyme'
import React from 'react'

import RawStockItem from '../RawStockItem'

const dispatchMock = jest.fn()

describe('src | components | pages | Offer | StockItem | RawStockItem ', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const initialProps = {
        closeInfo: jest.fn(),
        dispatch: dispatchMock,
        hasIban: false,
        history: { push: jest.fn() },
        isEventStock: false,
        stocks: [],
      }

      // when
      const wrapper = shallow(<RawStockItem {...initialProps} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('functions', () => {
    describe('handleSuccess', () => {
      it('redirect to gestion at patch success', () => {
        // given
        const state = {}
        const action = {
          config: {},
          payload: {
            datum: {
              id: 'K9',
            },
          },
          type: 'SUCCESS_DATA_PATCH_STOCKS/K9',
        }
        const historyMock = { push: jest.fn() }
        const initialProps = {
          closeInfo: jest.fn(),
          dispatch: jest.fn(),
          hasIban: false,
          history: historyMock,
          isEditing: false,
          isEventStock: false,
          offer: {
            id: 'TY',
          },
          stockPatch: {
            id: 'DG',
          },
          stocks: [],
        }

        // when
        const wrapper = shallow(<RawStockItem {...initialProps} />)
        wrapper.instance().handleSuccess(state, action)
        const expected = '/offres/TY?gestion'

        // then
        expect(historyMock.push).toHaveBeenCalledWith(expected)
      })
    })
  })
})
