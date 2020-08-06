import { shallow } from 'enzyme'
import Card from '../Card'
import React from 'react'

import Icon from '../../../../layout/Icon'
import { NavLink } from 'react-router-dom'

describe('src | components | pages | Home | Card', () => {
  let props

  beforeEach(() => {
    props = {
      navLink: 'http://nav.to/page',
      svg: 'my.svg',
      text: 'Fake text',
      title: 'Fake title',
    }
  })

  it('should display a link, an icon, a title and a text', () => {
    // when
    const wrapper = shallow(<Card {...props} />)

    // then
    const navLink = wrapper.find(NavLink)
    const logo = wrapper.find(Icon)
    const title = wrapper.find({ children: 'Fake title' })
    const text = wrapper.find({ children: 'Fake text' })
    expect(navLink.prop('to')).toBe('http://nav.to/page')
    expect(logo.prop('svg')).toBe('my.svg')
    expect(title).toHaveLength(1)
    expect(text).toHaveLength(1)
  })
})
