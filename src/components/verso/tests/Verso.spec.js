// $(yarn bin)/jest --env=jsdom ./src/components/verso/tests/Verso.spec.js --watch
import React from 'react'
import { shallow } from 'enzyme'

import Verso from '../Verso'
import VersoControl from '../verso-controls/VersoControl'
<<<<<<< HEAD
import VersoContentOfferContainer from '../verso-content/VersoContentOfferContainer'
import VersoContentTuto from '../verso-content/VersoContentTuto'
=======
import VersoInfoOffer from '../verso-content/verso-info-offer/VersoInfoOfferContainer'
import VersoTutoContent from '../verso-content/VersoTutoContent'
>>>>>>> (PC-1546): updated logic when checking if offer is finished, updated tests to simplify reading, added missing tests

const backgroundColor = '#ACE539'
const props = {
  areDetailsVisible: true,
  backgroundColor,
  contentInlineStyle: { backgroundColor, backgroundImage: 'any/image' },
  extraClassName: 'extra-classname',
  forceDetailsVisible: false,
  mediationId: 'AAA',
  offerName: 'Offer title',
  offerVenue: 'Offer subtitle',
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
  it('should show offer view', () => {
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
  it('should show tuto view', () => {
    // given
    const cprops = { ...props, isTuto: true }
    // when
    const wrapper = shallow(<Verso {...cprops} />)
    const infos = wrapper.find(VersoContentOfferContainer)
    const tuto = wrapper.find(VersoContentTuto)
    const controls = wrapper.find(VersoControl)
    // then
    expect(tuto).toHaveLength(1)
    expect(infos).toHaveLength(0)
    expect(controls).toHaveLength(0)
  })
})
