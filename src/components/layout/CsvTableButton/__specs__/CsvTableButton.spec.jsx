import { mount, shallow } from 'enzyme'
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
      const wrapper = mount(<CsvTableButton {...props} />)

      // then
      const submitButton = wrapper.find('button[type="button"]')
      expect(submitButton).toHaveLength(1)
      expect(submitButton.text()).toStrictEqual('foobar')
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
