import { shallow } from 'enzyme'
import React from 'react'

import DuoOffer from '../DuoOffer'

describe('src | components | DuoOffer', () => {
  it('when this offer is a not an "offre duo" should render nothing', () => {
    // given
    const props = {
      isDuoOffer: true,
      label: 'Vous pouvez réserver deux places.',
      offerId: 'AFZR',
    }

    // when
    const wrapper = shallow(<DuoOffer {...props} />)

    // then
    const sentence1 = wrapper.find({ children: 'duo' })
    const sentence2 = wrapper.find({ children: props.label })
    expect(sentence1).toHaveLength(1)
    expect(sentence2).toHaveLength(1)
  })

  it('when this offer is an "offre duo" should render picto and label', () => {
    // given
    const props = {
      isDuoOffer: false,
      label: 'Vous pouvez réserver deux places.',
      offerId: 'ABCD',
    }

    // when
    const wrapper = shallow(<DuoOffer {...props} />)

    // then
    const sentence1 = wrapper.find({ children: 'duo' })
    const sentence2 = wrapper.find({ children: props.label })
    expect(sentence1).toHaveLength(0)
    expect(sentence2).toHaveLength(0)
  })
})
