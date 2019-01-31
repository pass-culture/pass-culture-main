// jest --env=jsdom ./src/components/forms/inputs/tests/HiddenField --watch
import React from 'react'
import { shallow } from 'enzyme'

import CheckBoxField from '../CheckBoxField'

describe('src | components | forms | inputs | CheckBoxField', () => {
  it('should match snapshot with required props', () => {
    // given
    const props = { name: 'the-input-name' }

    // when
    const wrapper = shallow(<CheckBoxField {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
