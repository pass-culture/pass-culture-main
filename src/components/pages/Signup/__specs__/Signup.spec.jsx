import { shallow } from 'enzyme'
import React from 'react'
import { Route } from 'react-router-dom'

import Logo from 'components/layout/Logo'
import { campaignTracker } from 'tracking/mediaCampaignsTracking'
import { enzymeWaitFor } from 'utils/testHelpers'

import Signup from '../Signup'

describe('src | components | pages | Signup', () => {
  afterEach(jest.resetAllMocks)

  it('should render logo and and two routes', () => {
    // given
    const props = {
      location: {},
    }

    // when
    const wrapper = shallow(<Signup {...props} />)

    // then
    const logo = wrapper.find(Logo)
    const routes = wrapper.find(Route)
    expect(logo).toHaveLength(1)
    expect(routes.at(1).prop('path')).toBe('/inscription/confirmation')
  })

  it('should call media campaign tracker on mount only', async () => {
    // given
    const props = {
      location: {},
    }

    // when mount
    const wrapper = shallow(<Signup {...props} />)
    wrapper.update()

    // then
    await enzymeWaitFor(() => expect(campaignTracker.signUp).toHaveBeenCalledTimes(1))

    // when rerender
    wrapper.setProps(props)

    // then
    await enzymeWaitFor(() => expect(campaignTracker.signUp).toHaveBeenCalledTimes(1))
  })
})
