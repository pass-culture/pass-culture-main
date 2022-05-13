import LocationViewer from '../LocationViewer'
import React from 'react'
import { shallow } from 'enzyme'

describe('src | components | pages | Venue | fields | LocationViewer', () => {
  it('should diplay an input', () => {
    // when
    const wrapper = shallow(<LocationViewer />)

    // then
    const input = wrapper.find('input')
    expect(input.prop('value')).toBe('')
    expect(input.prop('readOnly')).toBe(true)
  })
})
