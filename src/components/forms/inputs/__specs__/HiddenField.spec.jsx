import React from 'react'
import { shallow } from 'enzyme'

import HiddenField from '../HiddenField'

describe('src | components | forms | inputs | HiddenField', () => {
  it('should match the snapshot', () => {
    // given
    const props = {
      name: 'the-input-name',
    }

    // when
    const wrapper = shallow(<HiddenField {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render an input of type hidden', () => {
    // given
    const props = {
      name: 'the-input-name',
    }

    // when
    const wrapper = shallow(<HiddenField {...props} />).dive()
    const inputElement = wrapper.find('input')

    // then
    expect(inputElement).toHaveLength(1)
    expect(inputElement.prop('name')).toStrictEqual('the-input-name')
    expect(inputElement.prop('validator')).toStrictEqual(expect.any(Function))
  })
})
