import { shallow } from 'enzyme'
import React from 'react'

import EventFields from '../EventFields'

describe('src | components | pages | Offer | StockItem | EventFields', () => {
  it('should match the snapshot', () => {
    // given
    const initialProps = {
      beginningMinDate: '2019-03-29T01:56:55.610Z',
      dispatch: jest.fn(),
      parseFormChild: jest.fn(),
    }

    // when
    const wrapper = shallow(<EventFields {...initialProps} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
