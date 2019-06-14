import React from 'react'
import { shallow } from 'enzyme'

import CheckBoxField from '../CheckBoxField'

describe('src | components | forms | inputs | CheckBoxField', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      children: <input type="checkbox" />,
      name: 'the-input-name',
    }

    // when
    const wrapper = shallow(<CheckBoxField {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
