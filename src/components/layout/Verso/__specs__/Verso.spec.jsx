import React from 'react'
import { shallow } from 'enzyme'

import Verso from '../Verso'
import VersoContentOfferContainer from '../VersoContent/VersoContentOffer/VersoContentOfferContainer'
import VersoControlsContainer from '../VersoControls/VersoControlsContainer'
import VersoHeaderContainer from '../VersoHeader/VersoHeaderContainer'
import LoaderContainer from '../../Loader/LoaderContainer'

describe('src | components | layout | Verso', () => {
  let props

  beforeEach(() => {
    props = {
      areDetailsVisible: true,
      backgroundColor: '#ACE539',
      extraClassNameVersoContent: 'verso-content',
      extraClassName: 'extra-classname',
      offerName: 'Offer title',
      offerType: 'EventType.SPECTACLE_VIVANT',
      offerVenueNameOrPublicName: 'Offer subtitle',
    }
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
    expect(firstDiv.prop('className')).toBe('verso is-overlay extra-classname ')
  })

  it('should show offer view', () => {
    // given - when
    const wrapper = shallow(<Verso {...props} />)

    // then
    const infos = wrapper.find(VersoContentOfferContainer)
    const controls = wrapper.find(VersoControlsContainer)
    expect(infos).toHaveLength(1)
    expect(controls).toHaveLength(1)
  })

  it('should render a VersoHeaderContainer with the right props', () => {
    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    const versoHeaderContainer = wrapper.find(VersoHeaderContainer)
    expect(versoHeaderContainer.prop('subtitle')).toBe('Offer subtitle')
    expect(versoHeaderContainer.prop('title')).toBe('Offer title')
    expect(versoHeaderContainer.prop('type')).toBe('EventType.SPECTACLE_VIVANT')
  })

  it('should render a loader while offer data are loading', () => {
    // given
    props.offerName = null

    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    const loaderContainer = wrapper.find(LoaderContainer)
    expect(loaderContainer).toHaveLength(1)
  })
})
