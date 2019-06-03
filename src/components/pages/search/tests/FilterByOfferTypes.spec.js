import { shallow } from 'enzyme'
import React from 'react'

import { FilterByOfferTypes } from '../FilterByOfferTypes'

describe('src | components | pages | search | FilterByOfferTypes', () => {
  const fakeMethod = jest.fn()
  let props

  beforeEach(() => {
    props = {
      filterActions: {
        add: fakeMethod,
        change: fakeMethod,
        remove: fakeMethod,
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
    it("should add Applaudir's category", () => {
      // given
      const category = 'Applaudir'

      // when
      const wrapper = shallow(<FilterByOfferTypes {...props} />)
      wrapper.instance().onChangeCategory(category)()

      // then
      expect(props.filterActions.add).toHaveBeenCalledWith(
        'categories',
        category
      )
      props.filterActions.add.mockClear()
    })

    it("should remove Applaudir's category", () => {
      // given
      props.filterState.params.categories = 'Toto,Applaudir,Jouer'
      const category = 'Applaudir'

      // when
      const wrapper = shallow(<FilterByOfferTypes {...props} />)
      wrapper.instance().onChangeCategory(category)()

      // then
      expect(props.filterActions.remove).toHaveBeenCalledWith(
        'categories',
        category
      )
      props.filterActions.remove.mockClear()
    })
  })

  describe('render()', () => {
    it('should have have seven checkboxes', () => {
      // when
      const wrapper = shallow(<FilterByOfferTypes {...props} />)
      const checkboxes = wrapper.find('input')

      // then
      expect(checkboxes).toHaveLength(7)
      props.typeSublabels.forEach((checkbox, index) => {
        expect(checkboxes.at(index).props().value).toBe(checkbox)
      })
    })

    it('should have Applaudir and Jouer checkboxes checked', () => {
      // given
      props.filterState.params.categories = 'Applaudir,Jouer'

      // when
      const wrapper = shallow(<FilterByOfferTypes {...props} />)
      const labels = wrapper.find('label')
      const expectedLabels = labels.reduce((accumulator, label) => {
        if (label.find('input').props().checked) {
          accumulator.push(label)
        }

        return accumulator
      }, [])

      // then
      expect(expectedLabels[0].find('i').is('.anticon-check-circle')).toBe(true)
      expect(expectedLabels[1].find('i').is('.anticon-check-circle')).toBe(true)
      expect(expectedLabels).toHaveLength(2)
    })
  })
})
