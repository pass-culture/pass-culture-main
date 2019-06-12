import { shallow } from 'enzyme'
import React from 'react'

import FilterByOfferTypes from '../FilterByOfferTypes'

describe('src | components | pages | search | FilterByOfferTypes', () => {
  let props

  beforeEach(() => {
    props = {
      filterActions: {
        add: jest.fn(),
        change: jest.fn(),
        remove: jest.fn(),
      },
      filterState: {
        isNew: false,
        params: {
          categories: null,
          date: null,
          distance: null,
          jours: null,
          latitude: null,
          longitude: null,
          'mots-cles': null,
          orderBy: 'offer.id+desc',
        },
      },
      typeSublabels: [
        'Applaudir',
        'Jouer',
        'Lire',
        'Pratiquer',
        'Regarder',
        'Rencontrer',
        'Écouter',
      ],
    }
  })

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<FilterByOfferTypes {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('onChangeCategory()', () => {
    it('should set the categories to Applaudir when I check Applaudir', () => {
      // given
      const category = 'Applaudir'
      const wrapper = shallow(<FilterByOfferTypes {...props} />)

      // when
      wrapper.instance().onChangeCategory(category)()

      // then
      expect(props.filterActions.add).toHaveBeenCalledWith(
        'categories',
        category
      )
    })

    it('should uncheck Applaudir within categories when I check Applaudir', () => {
      // given
      props.filterState.params.categories = 'Toto,Applaudir,Jouer'
      const category = 'Applaudir'
      const wrapper = shallow(<FilterByOfferTypes {...props} />)

      // when
      wrapper.instance().onChangeCategory(category)()

      // then
      expect(props.filterActions.remove).toHaveBeenCalledWith(
        'categories',
        category
      )
    })
  })

  describe('render()', () => {
    it('should have have seven checkboxes by default', () => {
      // given
      const wrapper = shallow(<FilterByOfferTypes {...props} />)

      // when
      const checkboxes = wrapper.find('input')

      // then
      expect(checkboxes).toHaveLength(7)
      props.typeSublabels.forEach((checkbox, index) => {
        expect(checkboxes.at(index).props().value).toBe(checkbox)
      })
    })

    it('should have Applaudir and Jouer checkboxes checked when I have "Applaudir,Jouer" in categories parameter', () => {
      // given
      props.filterState.params.categories = 'Applaudir,Jouer'
      const wrapper = shallow(<FilterByOfferTypes {...props} />)
      const labels = wrapper.find('label')
      const expectedLabels = labels.reduce((accumulator, label) => {
        if (label.find('input').props().checked) {
          accumulator.push(label)
        }

        return accumulator
      }, [])

      // when
      const firstLabel = expectedLabels[0]
        .find('i')
        .is('.icon-legacy-check-circled')
      const secondLabel = expectedLabels[1]
        .find('i')
        .is('.icon-legacy-check-circled')

      // then
      expect(firstLabel).toBe(true)
      expect(secondLabel).toBe(true)
      expect(expectedLabels).toHaveLength(2)
    })
  })
})
