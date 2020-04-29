import React from 'react'
import { shallow } from 'enzyme'

import ProfileMainView from '../ProfileMainView'

jest.mock('../../../../../../package.json', () => ({
  version: '78.0.0',
}))

describe('profileMainView', () => {
  it('should display the current version of package', () => {
    // Given
    const props = {
      currentUser: {},
    }
    const wrapper = shallow(<ProfileMainView {...props} />)

    // When
    const version = wrapper.find({ children: 'Version 78.0.0' })

    // Then
    expect(version).toHaveLength(1)
  })
})
