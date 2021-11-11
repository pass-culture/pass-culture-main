import { shallow } from 'enzyme'
import React from 'react'

import Ribbon from '../Ribbon'

describe('src | components | Ribbon', () => {
  it('should display a label', () => {
    // when
    const wrapper = shallow(<Ribbon />)

    // then
    const label = wrapper.find({ children: 'Annulé' })
    expect(label).toHaveLength(1)
  })
})
