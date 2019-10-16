import { mount } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import BookThisLink from '../BookThisLink'

describe('src | components | layout | Verso | VersoControls | booking | BookThisLink | BookThisLink', () => {
  let props

  beforeEach(() => {
    props = {
      destinationLink: 'http://fake-url.com',
      priceRange: [10, 30],
    }
  })

  describe('when the offer is bookable', () => {
    it('should render a price and label within link', () => {
      // given
      props.isNotBookable = false

      // when
      const wrapper = mount(
        <MemoryRouter>
          <BookThisLink {...props} />
        </MemoryRouter>
      )

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })

  describe('when the offer is not bookable', () => {
    it('should render a price and label within a wrapper', () => {
      // given
      props.isNotBookable = true

      // when
      const wrapper = mount(
        <MemoryRouter>
          <BookThisLink {...props} />
        </MemoryRouter>
      )

      // then
      expect(wrapper).toMatchSnapshot()
    })
  })
})
