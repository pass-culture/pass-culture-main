import React from 'react'
import { shallow } from 'enzyme'
import { UserIdentifierField } from '../UserIdentifierField'
import { InputField } from '../../../../../forms/inputs'

describe('src | components | pages | profile | UserIdentifierField', () => {
  let props

  beforeEach(() => {
    props = {
      isLoading: false,
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<UserIdentifierField {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should render an InputField component', () => {
    // when
    const wrapper = shallow(<UserIdentifierField {...props} />)

    // then
    const input = wrapper.find(InputField)
    expect(input).toHaveLength(1)
    expect(input.prop('required')).toBe(true)
    expect(input.prop('name')).toBe('publicName')
    expect(input.prop('label')).toBe('Votre identifiant')
    expect(input.prop('disabled')).toBe(false)
  })
})
