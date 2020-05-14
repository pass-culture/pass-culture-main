import { shallow } from 'enzyme'
import React from 'react'

import RelativeFooterContainer from '../../../../layout/RelativeFooter/RelativeFooterContainer'
import ListLinks from '../../ListLinks/ListLinks'
import ProfileHeader from '../../ProfileHeader/ProfileHeader'
import RemainingCredit from '../../RemainingCredit/RemainingCredit'
import ProfileMainView from '../ProfileMainView'
import User from '../../../../pages/profile/ValueObjects/User'

jest.mock('../../../../../../package.json', () => ({
  version: '78.0.0',
}))

describe('profile main view', () => {
  let props

  beforeEach(() => {
    props = {
      user: new User({}),
    }
  })

  it('should display header, remaining credit, my informations form and menu', () => {
    // When
    const wrapper = shallow(<ProfileMainView {...props} />)
    const ProfileHeaderWrapper = wrapper.find(ProfileHeader)
    const RemainingCreditWrapper = wrapper.find(RemainingCredit)
    const PersonalInformationsWrapper = wrapper.find(ListLinks)
    const RelativeFooterContainerWrapper = wrapper.find(RelativeFooterContainer)

    // Then
    expect(ProfileHeaderWrapper).toHaveLength(1)
    expect(RemainingCreditWrapper).toHaveLength(1)
    expect(PersonalInformationsWrapper).toHaveLength(1)
    expect(RelativeFooterContainerWrapper).toHaveLength(1)
  })

  it('should display the current version of package', () => {
    // When
    const wrapper = shallow(<ProfileMainView {...props} />)

    // Then
    const version = wrapper.find({ children: 'Version 78.0.0' })
    expect(version).toHaveLength(1)
  })

  it('should display the ministry of culture image', () => {
    // When
    const wrapper = shallow(<ProfileMainView {...props} />)

    // Then
    const logo = wrapper.find('img')
    expect(logo.prop('src')).toBe('/min-culture-rvb@2x.png')
    expect(logo.prop('alt')).toBe('')
  })
})
