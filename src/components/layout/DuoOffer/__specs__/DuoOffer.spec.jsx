import React from 'react'
import { shallow } from 'enzyme'

import DuoOffer from '../DuoOffer'

describe('src | components | layout | DuoOffer | DuoOffer', () => {
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
    expect(wrapper).toMatchSnapshot()
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
    expect(wrapper).toMatchSnapshot()
  })
})
