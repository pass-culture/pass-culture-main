import { shallow } from 'enzyme'
import React from 'react'

import ProfileMainView from '../ProfileMainView'
import ProfileHeader from '../../ProfileHeader/ProfileHeader'
import RelativeFooterContainer from '../../../../layout/RelativeFooter/RelativeFooterContainer'
import MesInformationsContainer from '../../MesInformations/MesInformationsContainer'
import RemainingCredit from '../../RemainingCredit/RemainingCredit'

jest.mock('../../../../../../package.json', () => ({
  version: '78.0.0',
}))

describe('profileMainView', () => {
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
    const MesInformationsContainerWrapper = wrapper.find(MesInformationsContainer)
    const RelativeFooterContainerWrapper = wrapper.find(RelativeFooterContainer)

    // Then
    expect(ProfileHeaderWrapper).toHaveLength(1)
    expect(RemainingCreditWrapper).toHaveLength(1)
    expect(MesInformationsContainerWrapper).toHaveLength(1)
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
    const logo = wrapper.find('img').props()
    expect(logo.src).toBe('/min-culture-rvb@2x.png')
    expect(logo.alt).toBe('')
  })
})
