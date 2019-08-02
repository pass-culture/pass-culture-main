import React from 'react'
import { shallow } from 'enzyme'

import CancelThisLink from '../CancelThisLink'
import Price from '../../../../../Price'

describe('src | components | layout | Verso | VersoControls | booking | CancelThisLink | CancelThisLink', () => {
  let props

  beforeEach(() => {
    props = {
      booking: {
        id: 'AAA',
        recommendation: {
          offerId: 'BBB',
        },
      },
      history: {
        push: jest.fn(),
      },
      location: {
        pathname: '',
        search: '',
      },
      match: { params: {} },
      offer: {},
      openCancelPopin: jest.fn(),
      stock: {},
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<CancelThisLink {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should display Price component, check icon, and label Annuler', () => {
      // when
      const wrapper = shallow(<CancelThisLink {...props} />)

      // then
      const price = wrapper.find(Price)
      const icon = wrapper.find('.icon-ico-check')
      const cancelLabel = wrapper.find('.pc-ticket-button-label')
      expect(icon).toHaveLength(1)
      expect(price).toHaveLength(1)
      expect(cancelLabel).toHaveLength(1)
      expect(cancelLabel.text()).toBe('Annuler')
    })

    it('should not contains a check icon when booking is cancelled', () => {
      // given
      props.booking.isCancelled = true

      // when
      const wrapper = shallow(<CancelThisLink {...props} />)
      const icon = wrapper.find('.icon-ico-check')

      // then
      expect(icon).toHaveLength(0)
    })
  })
})
