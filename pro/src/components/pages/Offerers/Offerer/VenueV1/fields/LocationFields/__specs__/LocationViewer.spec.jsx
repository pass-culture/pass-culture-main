/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt rtl "Gaël: migration from enzyme to RTL"
*/

import { shallow } from 'enzyme'
import React from 'react'

import LocationViewer from '../LocationViewer'

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
