import { shallow } from 'enzyme'
import React from 'react'

import ListLinks from '../../ListLinks/ListLinks'
import Header from '../../Header/Header'
import RemainingCredit from '../../RemainingCredit/RemainingCredit'
import MainView from '../MainView'
import User from '../../ValueObjects/User'
import NativeApplicationAdvertisement from '../../NativeApplicationAdvertisement/NativeApplicationAdvertisement'

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
    const NativeApplicationAdvertisementWrapper = wrapper.find(NativeApplicationAdvertisement)

    // Then
    expect(HeaderWrapper).toHaveLength(1)
    expect(RemainingCreditWrapper).toHaveLength(1)
    expect(PersonalInformationsWrapper).toHaveLength(1)
    expect(NativeApplicationAdvertisementWrapper).toHaveLength(0)
  })

  it('should not display remaining credit when user is not a beneficiary', () => {
    // When
    props.user = new User({ isBeneficiary: false })
    const wrapper = shallow(<MainView {...props} />)
    const RemainingCreditWrapper = wrapper.find(RemainingCredit)

    // Then
    expect(RemainingCreditWrapper).toHaveLength(0)
  })

  it('should display native application advertisement when user is not a beneficiary', () => {
    // When
    props.user = new User({ isBeneficiary: false })
    const wrapper = shallow(<MainView {...props} />)
    const NativeApplicationAdvertisementWrapper = wrapper.find(NativeApplicationAdvertisement)

    // Then
    expect(NativeApplicationAdvertisementWrapper).toHaveLength(1)
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
