import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Link, Router } from 'react-router-dom'

import OffererItem from '../OffererItem'

describe('src | components | pages | Offerers | OffererItem | OffererItem', () => {
  let props
  let history

  const dispatchMock = jest.fn()
  const parseMock = () => ({ 'mots-cles': null })
  const queryChangeMock = jest.fn()

  beforeEach(() => {
    props = {
      currentUser: {},
      isVenueCreationAvailable: true,
      dispatch: dispatchMock,
      offerer: {
        id: 'AE',
        name: 'Fake Name',
        nOffers: 0,
        isValidated: true,
      },
      pagination: {
        apiQuery: {
          keywords: null,
        },
      },
      query: {
        change: queryChangeMock,
        parse: parseMock,
      },
      location: {
        search: '',
      },
      venues: [
        {
          isDigital: true,
        },
      ],
      physicalVenues: [{}],
    }
    history = createBrowserHistory()
  })

  describe('render', () => {
    describe('when the offerer is waiting for approval', () => {
      it('should display an activation status message', () => {
        // given
        props.offerer = {
          id: 'AE',
          name: 'Fake Name',
          nOffers: 0,
          isValidated: false,
        }

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )
        const offererInformation = wrapper.find('#offerer-item-validation')

        // then
        expect(offererInformation.text()).toBe(
          'Structure en cours de validation par l’équipe pass Culture.'
        )
      })
    })

    describe('navigate to offerer caret', () => {
      it('should be displayed with right link', () => {
        // given
        // given
        props.offerer = {
          id: 'AE',
          isValidated: true,
          name: 'Validated Offerer',
          nOffers: 0,
          userHasAccess: true,
        }

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )
        const caret = wrapper.find('.caret')
        const navLink = caret.find(Link)

        // then
        expect(navLink.prop('to')).toBe('/structures/AE')
      })
    })

    describe('offerer name', () => {
      it('should be rendered with a link', () => {
        // given
        props.venues = [
          {
            isVirtual: true,
          },
        ]

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )
        const createOffer = wrapper.find('.name')
        const navLink = createOffer.find(Link)

        // then
        expect(navLink.text()).toBe('Fake Name')
        expect(navLink.prop('to')).toBe('/structures/AE')
      })
    })

    describe('create an offer', () => {
      describe('when offerer has only one virtual venue', () => {
        it('should display a link to create digital offer', () => {
          // given
          props.venues = [
            {
              isVirtual: true,
              id: 'DY',
            },
          ]
          // when
          const wrapper = mount(
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          )
          const createOffer = wrapper.find('#create-offer-action')
          const navLink = createOffer.find(Link)

          // then
          expect(navLink.text()).toBe('Nouvelle offre numérique')
          expect(navLink.prop('to')).toBe('/offres/creation?structure=AE&lieu=DY')
        })
      })

      describe('when offerer has one virtual venue and only one physical venue', () => {
        it('should display a link to create offer', () => {
          // given
          props.venues = [
            {
              isVirtual: true,
              id: 'DY',
            },
            {
              isVirtual: false,
              id: 'HD',
            },
          ]
          // when
          const wrapper = mount(
            <Router history={history}>
              <OffererItem {...props} />
            </Router>
          )
          const createOffer = wrapper.find('#create-offer-action')
          const navLink = createOffer.find(Link)

          // then
          expect(navLink.text()).toBe('Nouvelle offre')
          expect(navLink.prop('to')).toBe('/offres/creation?structure=AE')
        })
      })
    })

    describe('display offers total number', () => {
      it('should display offers total number', () => {
        // given
        props.offerer.nOffers = 42
        props.venues = [
          {
            isVirtual: true,
            id: 'DY',
          },
          {
            isVirtual: false,
            id: 'HD',
          },
        ]

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )

        const offersCount = wrapper.find({ children: '42 offres' })

        // then
        expect(offersCount).toHaveLength(1)
      })

      it('should display 0 offer when offerer has no offers', () => {
        // given
        props.offerer.nOffers = 0
        props.venues = [
          {
            isVirtual: true,
            id: 'DY',
          },
          {
            isVirtual: false,
            id: 'HD',
          },
        ]

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )

        const offersCount = wrapper.find({ children: '0 offre' })

        // then
        expect(offersCount).toHaveLength(1)
      })
    })

    describe('display physical venues total number', () => {
      it('should display total with a link to offers page', () => {
        // given
        props.offerer.nOffers = 42
        props.physicalVenues = [
          {
            isVirtual: false,
            id: 'DY',
          },
          {
            isVirtual: false,
            id: 'FL',
          },
          {
            isVirtual: false,
            id: 'DQ',
          },
        ]

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )
        const actions = wrapper.find('#count-venues-action')
        const navLink = actions.find(Link)

        // then
        expect(navLink.text()).toBe('3 lieux')
        expect(navLink.at(0).prop('to')).toBe('/structures/AE/')
      })

      it('should display 0 venue with a link to offerer page', () => {
        // given
        props.offerer.nOffers = 0
        props.physicalVenues = []

        // when
        const wrapper = mount(
          <Router history={history}>
            <OffererItem {...props} />
          </Router>
        )
        const actions = wrapper.find('#count-venues-action')
        const navLink = actions.find(Link)

        // then
        expect(navLink.text()).toBe('0 lieu')
        expect(navLink.at(0).prop('to')).toBe('/structures/AE/')
      })
    })

    describe('add new venue link', () => {
      it('should display a link to create a new venue', () => {
        // given
        props.offerer = {
          id: 'AE',
          name: 'Fake Name',
          nOffers: 0,
          isValidated: false,
        }

        // when
        const wrapper = shallow(<OffererItem {...props} />)
        const createVenueLink = wrapper.find('#create-venue-action').find(Link)

        // then
        expect(createVenueLink.prop('to')).toBe('/structures/AE/lieux/creation')
      })

      it('should redirect to unavailable page when venue creation is not available', () => {
        // given
        props.isVenueCreationAvailable = false
        props.offerer = {
          id: 'AE',
          name: 'Fake Name',
          nOffers: 0,
          isValidated: false,
        }

        // when
        const wrapper = shallow(<OffererItem {...props} />)
        const createVenueLink = wrapper.find('#create-venue-action').find(Link)

        // then
        expect(createVenueLink.prop('to')).toBe('/erreur/indisponible')
      })
    })
  })
})
