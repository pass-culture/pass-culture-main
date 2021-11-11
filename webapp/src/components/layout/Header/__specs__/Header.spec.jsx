import { shallow } from 'enzyme'
import React from 'react'

import BackLink from '../BackLink/BackLink'
import Header from '../Header'

describe('header', () => {
  let props

  beforeEach(() => {
    props = {
      history: {
        push: () => {},
        replace: () => {},
      },
      location: {
        pathname: '',
        search: '',
      },
      match: {
        params: {},
      },
      title: 'Fake header title',
    }
  })

  describe('render', () => {
    it('should display the header by default', () => {
      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const backLink = wrapper.find(BackLink)
      const h1 = wrapper.find('h1').text()
      expect(backLink).toHaveLength(0)
      expect(h1).toBe('Fake header title')
    })

    it('should display the back link', () => {
      // given
      props.backTo = '/fakeurl'

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const backLink = wrapper.find(BackLink)
      expect(backLink).toHaveLength(1)
    })

    it('should display a reset button when a reset function is provided', () => {
      // given
      props.reset = () => {}

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const reset = wrapper
        .findWhere(node => node.text() === 'Réinitialiser')
        .first()
        .find('button')
      expect(reset).toHaveLength(1)
      expect(reset.prop('className')).toBe('reset-button')
      expect(reset.prop('onClick')).toStrictEqual(props.reset)
      expect(reset.prop('type')).toBe('button')
    })

    it('should not display a reset button when no reset function is provided', () => {
      // given
      props.reset = null

      // when
      const wrapper = shallow(<Header {...props} />)

      // then
      const reset = wrapper
        .findWhere(node => node.text() === 'Réinitialiser')
        .first()
        .find('button')
      expect(reset).toHaveLength(0)
    })
  })
})
