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
        query: { context: () => ({}) },
        stockPatch: {},
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
    describe('handleRequestSuccess', () => {
      it('redirect to gestion at patch success', done => {
        // given
        const initialProps = {
          closeInfo: jest.fn(),
          dispatch: jest.fn(),
          hasIban: false,
          isEventStock: false,
          offer: {
            id: 'TY',
          },
          query: { changeToReadOnly: jest.fn(), context: () => ({}) },
          stockPatch: {
            id: 'DG',
          },
          stocks: [],
        }
        const wrapper = shallow(<RawStockItem {...initialProps} />)

        new Promise((resolve, reject) => {
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
          done()
        })
      })
    })
  })
})
