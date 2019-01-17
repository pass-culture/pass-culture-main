// jest --env=jsdom ./src/components/pages/activation/events/tests/email-button --watch
import React from 'react'
import { shallow } from 'enzyme'
import EmailButton from '../email-button'

describe('src | components | pages | activation | events | EmailButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<EmailButton />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
