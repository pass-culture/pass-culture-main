import React from 'react'
import { shallow } from 'enzyme'

import ProductFields from '../ProductFields'

describe('src | components | pages | Offer | StocksManager | StockItem | sub-components | fields | ProductFields', () => {
  it('should match the snapshot', () => {
    // given
    const initialProps = {
      closeInfo: jest.fn(),
      dispatch: jest.fn(),
      hasIban: false,
      parseFormChild: jest.fn(),
      showInfo: jest.fn(),
      venue: {},
    }

    // when
    const wrapper = shallow(<ProductFields {...initialProps} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
