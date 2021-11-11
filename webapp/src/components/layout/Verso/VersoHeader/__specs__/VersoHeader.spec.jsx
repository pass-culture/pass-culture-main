import React from 'react'
import { shallow } from 'enzyme'

import VersoHeader from '../VersoHeader'
import { ICONS_URL } from '../../../../../utils/config'

describe('src | components | layout | Verso | VersoHeader', () => {
  let props

  beforeEach(() => {
    props = {
      subtitle: 'Offer subtitle',
      title: 'Offer title',
      subcategory: { searchGroupName: 'SPECTACLE' },
    }
  })

  it('should display the offer title when provided', () => {
    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const offerName = wrapper.find('#verso-offer-name')
    expect(offerName.text()).toContain('Offer title')
  })

  it('should not display the offer title when not provided', () => {
    // given
    props.title = null

    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const offerName = wrapper.find('#verso-offer-name')
    expect(offerName).toHaveLength(0)
  })

  it('should display the offer subtitle when provided', () => {
    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const offerVenue = wrapper.find('#verso-offer-venue')
    expect(offerVenue.text()).toContain('Offer subtitle')
  })

  it('should not display the offer subtitle when not provided', () => {
    // given
    props.subtitle = null

    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const offerVenue = wrapper.find('#verso-offer-venue')
    expect(offerVenue).toHaveLength(0)
  })

  it('should display a picto matching offer type when provided', () => {
    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const picto = wrapper.find('#verso-offer-type-picto')
    expect(picto).toHaveLength(1)
    expect(picto.prop('alt')).toBe('')
    expect(picto.prop('src')).toBe(`${ICONS_URL}/picto-spectacle.svg`)
  })

  it('should not display a picto matching offer type when not provided', () => {
    // given
    props.subcategory = null

    // when
    const wrapper = shallow(<VersoHeader {...props} />)

    // then
    const picto = wrapper.find('#verso-offer-type-picto')
    expect(picto).toHaveLength(0)
  })
})
