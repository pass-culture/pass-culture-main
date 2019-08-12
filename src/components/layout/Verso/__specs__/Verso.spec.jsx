import React from 'react'
import { shallow } from 'enzyme'

import Verso from '../Verso'
import VersoContentOfferContainer from '../verso-content/VersoContentOffer/VersoContentOfferContainer'
import VersoContentTutoContainer from '../verso-content/VersoContentTuto/VersoContentTutoContainer'
import VersoControlsContainer from '../VersoControls/VersoControlsContainer'

const backgroundColor = '#ACE539'
const props = {
  areDetailsVisible: true,
  backgroundColor,
  contentInlineStyle: { backgroundColor, backgroundImage: 'any/image' },
  extraClassName: 'extra-classname',
  isTuto: false,
  mediationId: 'AAA',
  offerName: 'Offer title',
  offerVenueNameOrPublicName: 'Offer subtitle',
}

describe('src | components | verso | Verso', () => {
  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Verso {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should show offer view when is not tuto', () => {
    // when
    const wrapper = shallow(<Verso {...props} />)
    const infos = wrapper.find(VersoContentOfferContainer)
    const tuto = wrapper.find(VersoContentTutoContainer)
    const controls = wrapper.find(VersoControlsContainer)

    // then
    expect(tuto).toHaveLength(0)
    expect(infos).toHaveLength(1)
    expect(controls).toHaveLength(1)
  })

  it('should show tuto view when is tuto', () => {
    // given
    props.isTuto = true

    // when
    const wrapper = shallow(<Verso {...props} />)
    const infos = wrapper.find(VersoContentOfferContainer)
    const tuto = wrapper.find(VersoContentTutoContainer)
    const controls = wrapper.find(VersoControlsContainer)

    // then
    expect(tuto).toHaveLength(1)
    expect(infos).toHaveLength(0)
    expect(controls).toHaveLength(0)
  })
})
