import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import Teaser from '../Teaser'

describe('src | components | layout | Teaser | Teaser', () => {
  let props

  beforeEach(() => {
    props = {
      date: 'permanent',
      detailsUrl: 'fake/url',
      handleToggleItem: jest.fn(),
      humanizeRelativeDistance: '10 km',
      isEditMode: false,
      name: 'Fake offer name',
      offerId: 'MEFA',
      offerTypeLabel: 'Fake offer type label',
      status: [
        {
          label: 'Réservé',
          class: 'booked',
        },
      ],
      thumbUrl: null,
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Teaser {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    describe('when in a list mode', () => {
      it('should render a Link component and details of the favorite element', () => {
        // when
        const wrapper = shallow(<Teaser {...props} />)

        // then
        const link = wrapper.find(Link)
        const img = wrapper.find('img')
        const title = wrapper.find('.teaser-title').text()
        const type = wrapper.find('.teaser-wrapper > .teaser-sub-title').text()
        const date = wrapper.find('.teaser-wrapper > .teaser-date').text()
        const booked = wrapper.find('.teaser-booked').text()
        const distance = wrapper.find('.teaser-infos .teaser-distance').text()
        expect(link).toHaveLength(1)
        expect(img).toHaveLength(1)
        expect(title).toBe('Fake offer name')
        expect(type).toBe('Fake offer type label')
        expect(date).toBe('permanent')
        expect(booked).toBe('Réservé')
        expect(distance).toBe('10 km')
      })
    })

    describe('when in edit mode', () => {
      it('should render a checkbox', () => {
        // given
        props.isEditMode = true

        // when
        const wrapper = shallow(<Teaser {...props} />)

        // then
        const checkbox = wrapper.find('.teaser-checkbox')
        expect(checkbox).toHaveLength(1)
      })
    })

    describe('when click on checkbox', () => {
      it('should call handleToggleItem', () => {
        // given
        props.isEditMode = true
        const wrapper = shallow(<Teaser {...props} />)

        // when
        wrapper.find('.teaser-checkbox').simulate('click')

        // then
        expect(props.handleToggleItem).toHaveBeenCalledWith(props.offerId)
      })
    })
  })
})
