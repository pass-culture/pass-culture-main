import { shallow } from 'enzyme'
import React from 'react'

import StockItem from '../StockItem'

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
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('onFormSubmit()', () => {
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
