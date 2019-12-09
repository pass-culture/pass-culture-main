import { Link } from 'react-router-dom'
import { shallow } from 'enzyme'
import React from 'react'

import Icon from '../../../../layout/Icon/Icon'
import Results from '../Results'

describe('src | components | pages | search-algolia | Results | Results', () => {
  it('should have search-results when search is over', () => {
    // given
    const hits = [{
      _geoloc: {
        lat: 41.1,
        lng: 40.1
      },
      offer: {
        id: "E1",
        label: "Livre",
        name: "L'assommoir + !",
        thumbUrl: "http://linkToMyImage",
      },
      objectID: "BE3"
    }]

    // when
    const wrapper = shallow(<Results searchResults={ hits }/>)

    // then
    const results = wrapper.find('.search-results')
    const result = wrapper.find('.search-result')
    const image = wrapper.find(`div div > img`)
    const arrowIcon = wrapper.find(Icon)
    const detailsTitle= wrapper.find('div div > div > h2')
    const detailsLabel= wrapper.find('div div > div > p').first()
    const detailsDate= wrapper.find('div div > div > p').at(1)
    const detailsDistance= wrapper.find('div div > div > p').at(2)
    const link = wrapper.find(Link)
    expect(results).toHaveLength(1)
    expect(result).toHaveLength(1)
    expect(image.prop('src')).toBe('http://linkToMyImage')
    expect(detailsTitle.text()).toBe('L\'assommoir + !')
    expect(detailsLabel.text()).toBe('Livre')
    expect(detailsDate.text()).toBe('permanent')
    expect(detailsDistance.text()).toBe('-')
    expect(arrowIcon.prop('svg')).toBe('ico-next-S')
    expect(link.prop('to')).toBe('/recherche-algolia/details/E1/vide')
  })

  it('should have as many search-result as searchResults when search is over', () => {
    // given
    const hits = [{
        _geoloc: {
          lat: 41.1,
          lng: 40.1
        },
        offer: {
          id: "E1",
          label: "Livre",
          name: "L'assommoir + !",
          thumbUrl: "http://linkToMyImage",
        },
        objectID: "BE3"
      },
      {
        _geoloc: {
          lat: 41.1,
          lng: 40.1
        },
        offer: {
          id: "E1",
          label: "Livre",
          name: "L'assommoir + !",
          thumbUrl: "http://linkToMyImage",
        },
        objectID: "BE4"
      },
      {
        _geoloc: {
          lat: 41.1,
          lng: 40.1
        },
        offer: {
          id: "E1",
          label: "Livre",
          name: "L'assommoir + !",
          thumbUrl: "http://linkToMyImage",
        },
        objectID: "BE5"
      }
    ]

    // when
    const wrapper = shallow(<Results searchResults={ hits }/>)

    // then
    const result = wrapper.find('.search-result')
    expect(result).toHaveLength(3)
  })
})
