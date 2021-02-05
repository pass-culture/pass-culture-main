import { shallow } from 'enzyme'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { ReactComponent as OffersSvg } from 'components/layout/Header/assets/offers.svg'

import Card from '../Card'

describe('src | components | pages | Home | Card', () => {
  let props

  beforeEach(() => {
    props = {
      navLink: 'http://nav.to/page',
      svg: OffersSvg,
      text: 'Fake text',
      title: 'Fake title',
    }
  })

  it('should display a link, an icon, a title and a text', () => {
    // when
    const wrapper = shallow(<Card {...props} />)

    // then
    const navLink = wrapper.find(NavLink)
    const logo = wrapper.find(OffersSvg)
    const title = wrapper.find({ children: 'Fake title' })
    const text = wrapper.find({ children: 'Fake text' })
    expect(navLink.prop('to')).toBe('http://nav.to/page')
    expect(logo).toHaveLength(1)
    expect(title).toHaveLength(1)
    expect(text).toHaveLength(1)
  })
})
