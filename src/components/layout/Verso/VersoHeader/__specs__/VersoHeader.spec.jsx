import React from 'react'
import { shallow } from 'enzyme'

import VersoHeader from '../VersoHeader'
import { ICONS_URL } from '../../../../../utils/config'

describe('src | components | layout | Verso | VersoHeader', () => {
  let props

  beforeEach(() => {
    props = {
      backgroundColor: '#ACE539',
      history: { push: jest.fn() },
      location: {
        pathname: '',
        search: '',
      },
      match: { params: {} },
      subtitle: 'Offer subtitle',
      title: 'Offer title',
      type: 'EventType.SPECTACLE_VIVANT',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should display the offer name as title when provided', () => {
    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const offerName = wrapper.find('#verso-offer-name')
    expect(offerName.text()).toContain('Offer title')
  })

  it('should not display the offer name as title when not provided', () => {
    // given
    props.title = null

    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const offerName = wrapper.find('#verso-offer-name')
    expect(offerName).toHaveLength(0)
  })

  it('should display the offer venue name as subtitle when provided', () => {
    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const offerVenue = wrapper.find('#verso-offer-venue')
    expect(offerVenue.text()).toContain('Offer subtitle')
  })

  it('should not display the offer venue name as subtitle when not provided', () => {
    // given
    props.subtitle = null

    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const offerVenue = wrapper.find('#verso-offer-venue')
    expect(offerVenue).toHaveLength(0)
  })

  it('should display a triangle element with the right background', () => {
    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const triangle = wrapper.find('.verso-header')
    expect(triangle.prop('style')).toStrictEqual({ backgroundColor: '#ACE539' })
  })

  it('should display a picto matching offer type when provided', () => {
    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const picto = wrapper.find('#verso-offer-picto-type')
    expect(picto).toHaveLength(1)
    expect(picto.prop('alt')).toBe('EventType.SPECTACLE_VIVANT')
    expect(picto.prop('src')).toBe(`${ICONS_URL}/picto-spectacle.svg`)
  })

  it('should not display a picto matching offer type when not provided', () => {
    // given
    props.type = null

    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const picto = wrapper.find('#verso-offer-picto-type')
    expect(picto).toHaveLength(0)
  })
})
