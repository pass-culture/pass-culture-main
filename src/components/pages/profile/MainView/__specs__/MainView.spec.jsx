import { shallow } from 'enzyme'
import React from 'react'

import ListLinks from '../../ListLinks/ListLinks'
import Header from '../../Header/Header'
import RemainingCredit from '../../RemainingCredit/RemainingCredit'
import MainView from '../MainView'
import User from '../../ValueObjects/User'

jest.mock('../../../../../../package.json', () => ({
  version: '78.0.0',
}))

describe('profile main view', () => {
  let props

  beforeEach(() => {
    props = {
      user: new User({}),
      historyPush: jest.fn(),
    }
  })

  it('should display header, remaining credit, my informations form', () => {
    // When
    const wrapper = shallow(<MainView {...props} />)
    const HeaderWrapper = wrapper.find(Header)
    const RemainingCreditWrapper = wrapper.find(RemainingCredit)
    const PersonalInformationsWrapper = wrapper.find(ListLinks)

    // Then
    expect(HeaderWrapper).toHaveLength(1)
    expect(RemainingCreditWrapper).toHaveLength(1)
    expect(PersonalInformationsWrapper).toHaveLength(1)
  })

  it('should display the current version of package', () => {
    // When
    const wrapper = shallow(<MainView {...props} />)

    // Then
    const version = wrapper.find({ children: 'Version 78.0.0' })
    expect(version).toHaveLength(1)
  })

  it('should display the ministry of culture image', () => {
    // When
    const wrapper = shallow(<MainView {...props} />)

    // Then
    const logo = wrapper.find('img')
    expect(logo.prop('src')).toBe('/min-culture-rvb@2x.png')
    expect(logo.prop('alt')).toBe('')
  })
})
