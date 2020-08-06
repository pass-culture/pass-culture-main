import { shallow } from 'enzyme'
import React from 'react'

import CsvTableButton from '../CsvTableButton'

describe('src | components | layout | CsvTableButton', () => {
  let props

  beforeEach(() => {
    props = {
      children: 'foobar',
      history: {
        push: jest.fn(),
      },
      href: '/path-to-csv',
      location: {
        pathname: '/fake-url',
      },
    }
  })

  describe('render', () => {
    it('should render a button with the default props', () => {
      // when
      const wrapper = shallow(<CsvTableButton {...props} />)

      // then
      expect(wrapper.prop('className')).toBe('button is-primary is-flex-button')
      expect(wrapper.prop('onClick')).toStrictEqual(expect.any(Function))
      expect(wrapper.text()).toBe('foobar')
    })
  })

  describe('redirection', () => {
    it('should redirect to next url when clicking on button', () => {
      // given
      const wrapper = shallow(<CsvTableButton {...props} />)

      // when
      wrapper.simulate('click')

      // then
      expect(props.history.push).toHaveBeenCalledWith('/fake-url/detail', '/path-to-csv')
    })
  })
})
