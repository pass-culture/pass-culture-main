import { shallow } from 'enzyme'
import React from 'react'

import StockItem from '../StockItem'

const dispatchMock = jest.fn()

describe('src | components | pages | Offer | StockItem | StockItem ', () => {
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
})
