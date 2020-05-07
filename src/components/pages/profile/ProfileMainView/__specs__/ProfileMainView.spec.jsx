import { shallow } from 'enzyme'
import React from 'react'

import RelativeFooterContainer from '../../../../layout/RelativeFooter/RelativeFooterContainer'
import MyInformations from '../../MyInformations/MyInformations'
import ProfileHeader from '../../ProfileHeader/ProfileHeader'
import RemainingCredit from '../../RemainingCredit/RemainingCredit'
import ProfileMainView from '../ProfileMainView'

jest.mock('../../../../../../package.json', () => ({
  version: '78.0.0',
}))

describe('profile main view', () => {
  let props

  beforeEach(() => {
    props = {
      currentUser: {},
    }
  })

  it('should display header, remaining credit, my informations form and menu', () => {
    // When
    const wrapper = shallow(<ProfileMainView {...props} />)
    const ProfileHeaderWrapper = wrapper.find(ProfileHeader)
    const RemainingCreditWrapper = wrapper.find(RemainingCredit)
    const MyInformationsWrapper = wrapper.find(MyInformations)
    const RelativeFooterContainerWrapper = wrapper.find(RelativeFooterContainer)

    // Then
    expect(ProfileHeaderWrapper).toHaveLength(1)
    expect(RemainingCreditWrapper).toHaveLength(1)
    expect(MyInformationsWrapper).toHaveLength(1)
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
