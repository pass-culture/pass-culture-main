import React from 'react'
import { shallow } from 'enzyme'

import Verso from '../Verso'
import VersoContentOfferContainer from '../verso-content/VersoContentOffer/VersoContentOfferContainer'
import VersoContentTutoContainer from '../verso-content/VersoContentTuto/VersoContentTutoContainer'
import VersoControlsContainer from '../VersoControls/VersoControlsContainer'
import VersoHeaderContainer from '../verso-content/VersoHeaderContainer'
import AbsoluteFooterContainer from '../../AbsoluteFooter/AbsoluteFooterContainer'

describe('src | components | layout | Verso', () => {
  let props

  beforeEach(() => {
    props = {
      areDetailsVisible: true,
      backgroundColor: '#ACE539',
      contentInlineStyle: {
        backgroundColor: '#ACE539',
        backgroundImage: 'any/image',
      },
      extraClassName: 'extra-classname',
      isTuto: false,
      offerName: 'Offer title',
      offerVenueNameOrPublicName: 'Offer subtitle',
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  it('should render a div with the proper css classes when details are visible', () => {
    // given
    props.areDetailsVisible = true

    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    const firstDiv = wrapper.find('div').first()
    expect(firstDiv.prop('className')).toBe('verso is-overlay extra-classname flipped')
  })

  it('should render a div with the proper css classes when details are not visible', () => {
    // given
    props.areDetailsVisible = false

    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    const firstDiv = wrapper.find('div').first()
    expect(firstDiv.prop('className')).toBe('verso is-overlay extra-classname')
  })

  it('should show offer view when is tuto is false', () => {
    // given
    props.isTuto = false

    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    const infos = wrapper.find(VersoContentOfferContainer)
    const tuto = wrapper.find(VersoContentTutoContainer)
    const controls = wrapper.find(VersoControlsContainer)
    expect(tuto).toHaveLength(0)
    expect(infos).toHaveLength(1)
    expect(controls).toHaveLength(1)
  })

  it('should show tuto view when is tuto is true', () => {
    // given
    props.isTuto = true

    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    const infos = wrapper.find(VersoContentOfferContainer)
    const tuto = wrapper.find(VersoContentTutoContainer)
    const controls = wrapper.find(VersoControlsContainer)
    expect(tuto).toHaveLength(1)
    expect(infos).toHaveLength(0)
    expect(controls).toHaveLength(0)
  })

  it('should render a VersoHeaderContainer with the right props', () => {
    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    const versoHeaderContainer = wrapper.find(VersoHeaderContainer)
    expect(versoHeaderContainer.prop('backgroundColor')).toBe('#ACE539')
    expect(versoHeaderContainer.prop('subtitle')).toBe('Offer subtitle')
    expect(versoHeaderContainer.prop('title')).toBe('Offer title')
  })

  it('should render a AbsoluteFooterContainer with the right props', () => {
    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    const absoluteFooterContainer = wrapper.find(AbsoluteFooterContainer)
    expect(absoluteFooterContainer.prop('areDetailsVisible')).toBe(true)
    expect(absoluteFooterContainer.prop('borderTop')).toBe(true)
    expect(absoluteFooterContainer.prop('colored')).toBe(true)
    expect(absoluteFooterContainer.prop('id')).toBe('verso-footer')
  })

  it('should scroll to initial position when Verso component props are updated', () => {
    // given
    const scrollTo = jest.fn()
    const wrapper = shallow(<Verso {...props} />)
    wrapper.instance()['versoWrapper'] = {
      current: {
        scrollTo,
      },
    }
    props.areDetailsVisible = false

    // when
    wrapper.setProps({ ...props })

    // then
    expect(scrollTo).toHaveBeenCalledWith(0, 0)
  })
})
