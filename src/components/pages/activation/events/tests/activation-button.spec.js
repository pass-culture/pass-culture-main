// jest --env=jsdom ./src/components/pages/activation/events/tests/activation-button --watch
import React from 'react'
import { shallow } from 'enzyme'
import ActivationOnlineButton from '../activation-button'

describe('src | components | pages | activation | events | ActivationOnlineButton', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // when
      const wrapper = shallow(<ActivationOnlineButton />)
      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
})
