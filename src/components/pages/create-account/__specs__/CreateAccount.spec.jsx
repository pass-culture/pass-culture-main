import { shallow } from 'enzyme'
import React from 'react'
import { Route } from 'react-router-dom'
import { createMemoryHistory } from 'history'

import CreateAccount from '../CreateAccount'

describe('create account page', () => {
  it('should allow redirection to specific routes', () => {
    // when
    const wrapper = shallow(<CreateAccount history={createMemoryHistory()} />)

    // then
    const routes = wrapper.find(Route)
    expect(routes.at(0).prop('path')).toBe('/verification-eligibilite/eligible')
    expect(routes.at(1).prop('path')).toBe('/verification-eligibilite/departement-non-eligible')
    expect(routes.at(2).prop('path')).toBe('/verification-eligibilite/pas-eligible')
    expect(routes.at(3).prop('path')).toBe('/verification-eligibilite/bientot')
    expect(routes.at(4).prop('path')).toBe('/verification-eligibilite/trop-tot')
    expect(routes.at(5).prop('path')).toBe('/verification-eligibilite/gardons-contact')
    expect(routes.at(6).prop('path')).toBe('/verification-eligibilite')
  })
})
