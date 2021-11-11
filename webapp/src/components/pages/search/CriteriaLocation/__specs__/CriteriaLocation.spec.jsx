import { shallow } from 'enzyme'
import React from 'react'
import Header from '../../../../layout/Header/Header'
import { GEOLOCATION_CRITERIA } from '../../Criteria/criteriaEnums'
import CriteriaLocation from '../CriteriaLocation'
import { Criteria } from '../../Criteria/Criteria'
import Place from '../Place/Place'
import { createBrowserHistory } from 'history'

describe('components | CriteriaLocation', () => {
  let props

  beforeEach(() => {
    props = {
      activeCriterionLabel: 'Autour de moi',
      backTo: '/recherche',
      criteria: GEOLOCATION_CRITERIA,
      geolocation: {
        latitude: 40,
        longitude: 2,
      },
      history: createBrowserHistory(),
      match: {
        params: {},
      },
      onPlaceSelection: jest.fn(),
      onCriterionSelection: jest.fn(),
      place: null,
      title: 'Où',
    }
  })

  describe('when on criteria location page', () => {
    it('should render a Header component with the right props', () => {
      // when
      const wrapper = shallow(<CriteriaLocation {...props} />)

      // then
      const header = wrapper.find(Header)
      expect(header).toHaveLength(1)
      expect(header.prop('backTo')).toStrictEqual('/recherche')
      expect(header.prop('history')).toStrictEqual(props.history)
      expect(header.prop('location')).toStrictEqual(props.history.location)
      expect(header.prop('match')).toStrictEqual(props.match)
      expect(header.prop('title')).toStrictEqual(props.title)
    })

    it('should render a Criteria component with the right props', () => {
      // when
      const wrapper = shallow(<CriteriaLocation {...props} />)

      // then
      const criteria = wrapper.find(Criteria)
      expect(criteria.prop('activeCriterionLabel')).toStrictEqual(props.activeCriterionLabel)
      expect(criteria.prop('backTo')).toStrictEqual(props.backTo)
      expect(criteria.prop('criteria')).toStrictEqual(props.criteria)
      expect(criteria.prop('history')).toStrictEqual(props.history)
      expect(criteria.prop('match')).toStrictEqual(props.match)
      expect(criteria.prop('onCriterionSelection')).toStrictEqual(expect.any(Function))
      expect(criteria.prop('title')).toStrictEqual(props.title)
    })

    it('should render an Icon component for the warning message', () => {
      // when
      const wrapper = shallow(<CriteriaLocation {...props} />)

      // then
      const icon = wrapper.find('Icon[svg="ico-alert"]')
      expect(icon).toHaveLength(1)
    })

    it('should render a warning message', () => {
      // when
      const wrapper = shallow(<CriteriaLocation {...props} />)

      // then
      const message = wrapper.find({
        children:
          'Seules les offres Sorties et Physiques seront affichées pour une recherche avec une localisation',
      })
      expect(message).toHaveLength(1)
    })

    it('should render an Icon component for search by place', () => {
      // when
      const wrapper = shallow(<CriteriaLocation {...props} />)

      // then
      const icon = wrapper.find('Icon[svg="ico-there"]')
      expect(icon).toHaveLength(1)
    })

    it('should render a button to redirect to search place page', () => {
      // given
      props.history.push('/recherche/criteres-localisation')

      // when
      const wrapper = shallow(<CriteriaLocation {...props} />)

      // then
      const chooseAPlaceButton = wrapper.find({ children: 'Choisir un lieu' })
      expect(chooseAPlaceButton).toHaveLength(1)
    })

    it('should render a button with place name to redirect to search place page when place was already filled', () => {
      // given
      props.place = {
        name: {
          long: 'Paris',
          short: 'Paris',
        },
      }
      props.history.push('/recherche/criteres-localisation')

      // when
      const wrapper = shallow(<CriteriaLocation {...props} />)

      // then
      const chooseAPlaceButton = wrapper.find({ children: 'Paris' })
      expect(chooseAPlaceButton).toHaveLength(1)
    })

    it('should redirect to search place page when clicking on "Choisir un lieu"', () => {
      // given
      props.history.push('/recherche/criteres-localisation')
      jest.spyOn(props.history, 'push').mockImplementation(() => jest.fn())
      const wrapper = shallow(<CriteriaLocation {...props} />)
      const chooseAPlaceButton = wrapper.find({ children: 'Choisir un lieu' })

      // when
      chooseAPlaceButton.simulate('click')

      // then
      expect(props.history.push).toHaveBeenCalledWith('/recherche/criteres-localisation/place')
    })
  })

  describe('when on place location page', () => {
    it('should render a Place component with the right props', () => {
      // given
      props.history.location.pathname =
        '/recherche/resultats/filtres/localisation/place?mots-cles=livre'

      // when
      const wrapper = shallow(<CriteriaLocation {...props} />)

      // then
      const place = wrapper.find(Place)
      expect(place).toHaveLength(1)
      expect(place.prop('backTo')).toStrictEqual(
        '/recherche/resultats/filtres/localisation?mots-cles=livre'
      )
      expect(place.prop('history')).toStrictEqual(props.history)
      expect(place.prop('match')).toStrictEqual(props.match)
      expect(place.prop('title')).toStrictEqual('Choisir un lieu')
      expect(place.prop('onPlaceSelection')).toStrictEqual(expect.any(Function))
    })
  })
})
