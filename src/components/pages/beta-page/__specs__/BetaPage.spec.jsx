import React from 'react'
import { shallow } from 'enzyme'

import BetaPage from '../BetaPage'

describe('src | components | pages | BetaPage', () => {
  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<BetaPage />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
