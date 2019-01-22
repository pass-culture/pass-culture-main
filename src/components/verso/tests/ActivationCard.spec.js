// jest --env=jsdom ./src/components/verso/tests/ActivationCard --watch
import React from 'react'
import { shallow } from 'enzyme'
import ActivationCard from '../ActivationCard'

describe('src | components | verso | ActivationCard', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<ActivationCard />)
    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
