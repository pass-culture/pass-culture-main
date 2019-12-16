import { shallow } from 'enzyme'
import React from 'react'
import Icon from '../Icon'

jest.mock('../../../../utils/config', () => ({
  ICONS_URL: 'path/to/icons',
}))

describe('src | components | layout | Icon', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Icon />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render img tag with given alt value', () => {
    const alt = 'alt value'

    // When
    const wrapper = shallow(<Icon alt={alt} />)

    // Then
    expect(wrapper.type()).toBe('img')
    expect(wrapper.prop('alt')).toBe(alt)
  })

  it('should render component with given className', () => {
    // Given
    const classNameProp = 'className'

    // When
    const wrapper = shallow(<Icon className={classNameProp} />)

    // Then
    expect(wrapper.prop('className')).toBe(classNameProp)
  })

  it('should set alt as empty string if no alt is given', () => {
    // When
    const wrapper = shallow(<Icon />)

    // Then
    expect(wrapper.prop('alt')).toBe('')
  })

  it('should render component with SVG file from given name as src', () => {
    // Given
    const fileName = 'fileName'

    // When
    const wrapper = shallow(<Icon svg={fileName} />)

    // Then
    expect(wrapper.prop('src')).toBe(`path/to/icons/${fileName}.svg`)
  })

  it('should render component with PNG file from given name as src', () => {
    // Given
    const fileName = 'fileName'

    // When
    const wrapper = shallow(<Icon png={fileName} />)

    // Then
    expect(wrapper.prop('src')).toBe(`path/to/icons/${fileName}.png`)
  })
})
