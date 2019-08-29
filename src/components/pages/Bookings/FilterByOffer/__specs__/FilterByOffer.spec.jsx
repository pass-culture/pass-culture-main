import React from 'react'
import { shallow } from 'enzyme/build'

import FilterByDateContainer from '../../FilterByDate/FilterByDateContainer'
import FilterByOffer from '../FilterByOffer'

describe('src | components | pages | FilterByOffer | FilterByOffer', () => {
  let props

  beforeEach(() => {
    props = {
      isFilteredByDigitalVenues: false,
      loadOffers: jest.fn(),
      offers: [],
      offersOptions: [
        {
          id: 'all',
          name: 'Toutes les offres',
        },
        {
          id: 'CY',
          name: 'Spectacle de danse',
        },
      ],
      updateOfferId: jest.fn(),
      showDateSection: false,
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<FilterByOffer {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('the date section', () => {
      it('should be hidden when `all offer is selected', () => {
        // when
        const wrapper = shallow(<FilterByOffer {...props} />)

        // then
        const filterByDateContainer = wrapper.find(FilterByDateContainer)
        expect(filterByDateContainer).toHaveLength(0)
      })

      it('should display offer section when a specific offer is selected', () => {
        // given
        props.showDateSection = true

        // when
        const wrapper = shallow(<FilterByOffer {...props} />)

        // then
        const filterByDateContainer = wrapper.find(FilterByDateContainer)
        expect(filterByDateContainer).toHaveLength(1)
      })
    })

    describe('labels', () => {
      it('should display `Offre` when isFilteredByDigitalVenues is false', () => {
        // given
        props.isFilteredByDigitalVenues = false

        // when
        const wrapper = shallow(<FilterByOffer {...props} />)

        // then
        const mainListTitle = wrapper.find('.main-list-title').text()
        expect(mainListTitle).toBe('Offre')
      })

      it('should display `Offre numérique` when isFilteredByDigitalVenues is true', () => {
        // given
        props.isFilteredByDigitalVenues = true

        // when
        const wrapper = shallow(<FilterByOffer {...props} />)

        // then
        const mainListTitle = wrapper.find('.main-list-title').text()
        expect(mainListTitle).toBe('Offre numérique')
      })

      it("should display `Télécharger les réservations pour l'offre :` when isFilteredByDigitalVenues is false", () => {
        // given
        props.isFilteredByDigitalVenues = false

        // when
        const wrapper = shallow(<FilterByOffer {...props} />)

        // then
        const label = wrapper.find('label')
        expect(label.at(0).text()).toBe("Télécharger les réservations pour l'offre :")
      })

      it("should display `Télécharger les réservations pour l'offre numérique:` when isFilteredByDigitalVenues is true", () => {
        // given
        props.isFilteredByDigitalVenues = true

        // when
        const wrapper = shallow(<FilterByOffer {...props} />)

        // then
        const label = wrapper.find('label')
        expect(label.at(0).text()).toBe("Télécharger les réservations pour l'offre numérique :")
      })
    })

    describe('selector', () => {
      it('should render a select input for offer with 3 options', () => {
        // when
        const wrapper = shallow(<FilterByOffer {...props} />)

        // then
        const selectOffer = wrapper.find('#offers')
        expect(selectOffer.prop('className')).toBe('pc-selectbox')
        expect(selectOffer.prop('id')).toBe('offers')
        expect(selectOffer.prop('onBlur')).toStrictEqual(expect.any(Function))
        expect(selectOffer.prop('onChange')).toStrictEqual(expect.any(Function))
        const options = selectOffer.find('option')
        expect(options).toHaveLength(3)
        expect(options.at(0).prop('disabled')).toBe(true)
        expect(options.at(0).prop('label')).toBe(' - Choisissez une offre dans la liste - ')
        expect(options.at(0).prop('selected')).toBe(true)
        expect(options.at(1).key()).toBe('all')
        expect(options.at(1).prop('value')).toBe('all')
        expect(options.at(2).key()).toBe('CY')
        expect(options.at(2).prop('value')).toBe('CY')
      })
    })
    
  })
})
