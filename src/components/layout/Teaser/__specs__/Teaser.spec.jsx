import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import Teaser from '../Teaser'
import Icon from '../../Icon/Icon'

describe('src | components | layout | Teaser | Teaser', () => {
  let props

  beforeEach(() => {
    props = {
      date: 'permanent',
      detailsUrl: 'fake/url',
      handleToggleTeaser: jest.fn(),
      humanizeRelativeDistance: '10 km',
      isEditMode: false,
      name: 'Fake offer name',
      offerId: 'MEFA',
      offerTypeLabel: 'Fake offer type label',
      statuses: [
        {
          label: 'Réservé',
          class: 'booked',
        },
      ],
      thumbUrl: null,
      trackConsultOffer: jest.fn(),
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Teaser {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('when in a list mode', () => {
    it('should render a Link and Icon', () => {
      // when
      const wrapper = shallow(<Teaser {...props} />)

      // then
      expect(wrapper.find(Link)).toHaveLength(1)
      expect(wrapper.find(Icon)).toHaveLength(1)
      expect(wrapper.find('[type="checkbox"]')).toHaveLength(0)
    })
  })

  describe('when in edit mode', () => {
    it('should render a checkbox', () => {
      // given
      props.isEditMode = true

      // when
      const wrapper = shallow(<Teaser {...props} />)

      // then
      expect(wrapper.find(Link)).toHaveLength(0)
      expect(wrapper.find(Icon)).toHaveLength(0)
      expect(wrapper.find('[type="checkbox"]')).toHaveLength(1)
    })
  })

  describe('when click on checkbox', () => {
    it('should call handleToggleTeaser', () => {
      // given
      props.isEditMode = true
      const wrapper = shallow(<Teaser {...props} />)

      // when
      wrapper.find('[type="checkbox"]').simulate('click')

      // then
      expect(props.handleToggleTeaser).toHaveBeenCalledWith(props.offerId)
    })
  })
})
