import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import MyFavorite from '../MyFavorite'

describe('src | components | pages | my-favorites | MyFavorite | MyFavorite', () => {
  let props

  beforeEach(() => {
    props = {
      date: 'permanent',
      detailsUrl: 'fake/url',
      handleToggleFavorite: jest.fn(),
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
    const wrapper = shallow(<MyFavorite {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render()', () => {
    describe('when I am in a list mode', () => {
      it('should render a Link', () => {
        // when
        const wrapper = shallow(<MyFavorite {...props} />)

        // then
        const link = wrapper.find(Link)
        const img = wrapper.find('img')
        const title = wrapper.find('.teaser-title').text()
        const type = wrapper.find('.mf-wrapper > .teaser-sub-title').text()
        const date = wrapper.find('.mf-wrapper > .teaser-date').text()
        const booked = wrapper.find('.mf-booked').text()
        const distance = wrapper.find('.mf-infos .teaser-distance').text()
        expect(link).toHaveLength(1)
        expect(img).toHaveLength(0)
        expect(title).toBe('Fake offer name')
        expect(type).toBe('Fake offer type label')
        expect(date).toBe('permanent')
        expect(booked).toBe('Réservé')
        expect(distance).toBe('10 km')
      })
    })

    describe('when I am in an edit mode', () => {
      it('should render a checkbox', () => {
        // given
        props.isEditMode = true

        // when
        const wrapper = shallow(<MyFavorite {...props} />)

        // then
        const checkbox = wrapper.find('.teaser-checkbox')
        const input = wrapper.find('input')
        const img = wrapper.find('img')
        const title = wrapper.find('.teaser-title').text()
        const type = wrapper.find('.mf-wrapper > .teaser-sub-title').text()
        const date = wrapper.find('.mf-wrapper > .teaser-date').text()
        const booked = wrapper.find('.mf-booked').text()
        const distance = wrapper.find('.mf-infos .teaser-distance').text()
        expect(checkbox).toHaveLength(1)
        expect(input).toHaveLength(1)
        expect(img).toHaveLength(0)
        expect(title).toBe('Fake offer name')
        expect(type).toBe('Fake offer type label')
        expect(date).toBe('permanent')
        expect(booked).toBe('Réservé')
        expect(distance).toBe('10 km')
      })
    })

    describe('when click on checkbox', () => {
      it('should call handleToggleFavorite', () => {
        // given
        props.isEditMode = true
        const wrapper = shallow(<MyFavorite {...props} />)

        // when
        wrapper.find('.teaser-checkbox').simulate('click')

        // then
        expect(props.handleToggleFavorite).toHaveBeenCalledWith(props.offerId)
      })
    })
  })
})
