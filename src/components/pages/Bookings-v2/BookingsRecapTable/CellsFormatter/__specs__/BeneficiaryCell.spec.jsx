import { shallow } from 'enzyme/build'
import BeneficiaryCell from '../BeneficiaryCell'
import React from 'react'

describe('components | BeneficiaryCell', () => {
  it('should render a div with two span, one with firstname and lastname and the other the email address', () => {
    // Given
    const props = {
      beneficiaryInfos: {
        firstname: 'Laurent',
        lastname: 'Durond',
        email: 'email@example.com',
      },
    }

    // When
    const wrapper = shallow(<BeneficiaryCell {...props} />)
    const spans = wrapper.find('span')
    const nameSpan = spans.find('span').at(0)
    const emailAddressSpan = spans.find('span').at(1)

    // Then
    expect(spans).toHaveLength(2)
    expect(nameSpan.text()).toBe('Laurent Durond')
    expect(emailAddressSpan.text()).toBe('email@example.com')
  })
})
