import { shallow } from 'enzyme'
import React from 'react'
import Icon from '../Icon'

jest.mock('../../../../utils/config', () => ({
  ICONS_URL: 'path/to/icons',
}))

describe('src | components | layout | Icon', () => {
  let props

  beforeEach(() => {
    props = {
      svg: 'fake-svg',
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Icon {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render img tag with given alt value', () => {
    props.alt = 'alt value'

    // When
    const wrapper = shallow(<Icon {...props} />)

    // Then
    expect(wrapper.type()).toBe('img')
    expect(wrapper.prop('alt')).toBe('alt value')
  })

  it('should render component with given className', () => {
    // Given
    props.className = 'fake-class'

    // When
    const wrapper = shallow(<Icon {...props} />)

    // Then
    expect(wrapper.prop('className')).toBe('fake-class')
  })

  it('should set alt as empty string if no alt is given', () => {
    // When
    const wrapper = shallow(<Icon {...props} />)

    // Then
    expect(wrapper.prop('alt')).toBe('')
  })

  it('should render component with SVG file from given name as src', () => {
    // When
    const wrapper = shallow(<Icon {...props} />)

    // Then
    expect(wrapper.prop('src')).toBe('path/to/icons/fake-svg.svg')
  })
})
