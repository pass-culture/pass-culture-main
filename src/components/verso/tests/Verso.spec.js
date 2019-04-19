import React from 'react'
import { shallow } from 'enzyme'

import Verso from '../Verso'
import VersoControl from '../verso-controls/VersoControlContainer'
import VersoContentOfferContainer from '../verso-content/verso-content-offer/VersoContentOfferContainer'
import VersoContentTuto from '../verso-content/VersoContentTuto'

const backgroundColor = '#ACE539'
const props = {
  areDetailsVisible: true,
  backgroundColor,
  contentInlineStyle: { backgroundColor, backgroundImage: 'any/image' },
  extraClassName: 'extra-classname',
  forceDetailsVisible: false,
  mediationId: 'AAA',
  offerName: 'Offer title',
  offerVenueNameOrPublicName: 'Offer subtitle',
}

describe('src | components | verso | Verso', () => {
  it('should match snapshot', () => {
    // given
    const cprops = { ...props, isTuto: false }

    // when
    const wrapper = shallow(<Verso {...cprops} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should show offer view when is not tuto', () => {
    // given
    const cprops = { ...props, isTuto: false }

    // when
    const wrapper = shallow(<Verso {...cprops} />)
    const infos = wrapper.find(VersoContentOfferContainer)
    const tuto = wrapper.find(VersoContentTuto)
    const controls = wrapper.find(VersoControl)

    // then
    expect(tuto).toHaveLength(0)
    expect(infos).toHaveLength(1)
    expect(controls).toHaveLength(1)
  })

  it('should show tuto view when is tuto', () => {
    // given
    const cprops = {
      ...props,
      imageURL: 'https://example.net/tuto/image.png',
      isTuto: true,
    }

    // when
    const wrapper = shallow(<Verso {...cprops} />)
    const infos = wrapper.find(VersoContentOfferContainer)
    const tuto = wrapper.find(VersoContentTuto)
    const controls = wrapper.find(VersoControl)

    // then
    expect(tuto).toHaveLength(1)
    expect(tuto.props()).toHaveProperty(
      'imageURL',
      'https://example.net/tuto/image.png'
    )
    expect(infos).toHaveLength(0)
    expect(controls).toHaveLength(0)
  })
})
