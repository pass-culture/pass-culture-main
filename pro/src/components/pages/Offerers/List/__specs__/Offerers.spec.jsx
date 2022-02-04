import { shallow } from 'enzyme'
import React from 'react'
import { Link } from 'react-router-dom'

import Titles from 'components/layout/Titles/Titles'

import OffererItemContainer from '../OffererItem/OffererItemContainer'
import PendingOffererItem from '../OffererItem/PendingOffererItem'
import Offerers from '../Offerers'

describe('src | components | Offerers', () => {
  let props

  beforeEach(() => {
    props = {
      closeNotification: jest.fn(),
      currentUser: {},
      isOffererCreationAvailable: true,
      loadOfferers: jest.fn(),
      location: {
        search: '',
      },
      offerers: [{ id: 'AE', siren: '1234567' }],
      query: {
        parse: () => ({ 'mots-cles': null }),
      },
      resetLoadedOfferers: jest.fn(),
      showNotification: jest.fn(),
    }
  })

  describe('render', () => {
    describe('subtitle message', () => {
      describe('when the isOffererCreationAvailable feature is activated', () => {
        it('should display a link to create an offer', () => {
          // when
          const wrapper = shallow(<Offerers {...props} />)
          const links = wrapper.find('a')

          // then
          expect(links.at(0).text()).toBe('créer un nouveau lieu')
          expect(links.at(0).prop('href')).toBe('/structures/AE/lieux/creation')
        })
      })

      describe('when the isOffererCreationAvailable feature is disabled', () => {
        it('should display a link to create an offer', () => {
          // given
          props.isOffererCreationAvailable = false

          // when
          const wrapper = shallow(<Offerers {...props} />)
          const links = wrapper.find('a')

          // then
          expect(links.at(0).text()).toBe('créer un nouveau lieu')
          expect(links.at(0).prop('href')).toBe('/erreur/indisponible')
        })
      })
    })

    describe('should pluralize offerers menu link', () => {
      it('should display Structure juridique when one offerer', () => {
        // given
        props.currentUser = {}
        props.offerers = [{ id: 'AE' }]

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const titles = wrapper.find('Titles').props()

        // then
        expect(titles.title).toBe('Structure juridique')
      })

      it('should display Structures juridiques when many offerers', () => {
        // given
        props.currentUser = {}
        props.offerers = [{ id: 'AE' }, { id: 'AF' }]

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const titles = wrapper.find('Titles').props()

        // then
        expect(titles.title).toBe('Structures juridiques')
      })
    })

    describe('when leaving page', () => {
      it('should not close notifcation', () => {
        // given
        props = { ...props, closeNotification: jest.fn() }
        const wrapper = shallow(<Offerers {...props} />)

        // when
        wrapper.unmount()

        // then
        expect(props.closeNotification).not.toHaveBeenCalled()
      })

      it('should not fail on null notifcation', () => {
        // given
        props = {
          ...props,
          closeNotification: jest.fn(),
          notification: null,
        }
        const wrapper = shallow(<Offerers {...props} />)

        // when
        wrapper.unmount()

        // then
        expect(props.closeNotification).not.toHaveBeenCalledWith()
      })
    })

    describe('when displaying the list of offerers', () => {
      describe('when the offerer is active and the user has access to it', () => {
        it('should render an active offerer item in the list for each activated offerer', () => {
          // given
          const offerer = { id: 'B2', isValidated: true, userHasAccess: true }
          props.offerers = [offerer]

          // when
          const wrapper = shallow(<Offerers {...props} />)

          // then
          const offererItem = wrapper.find(OffererItemContainer)
          expect(offererItem).toHaveLength(1)
          expect(offererItem.at(0).prop('offerer')).toStrictEqual(offerer)
        })
      })

      describe('when offerer is not active for the user', () => {
        describe('when the offerer is not active', () => {
          it('should render a pending offerer item', () => {
            // given
            const offerer = {
              id: 'B2',
              siren: '1431',
              isValidated: false,
              userHasAccess: true,
            }
            props.offerers = [offerer]

            // when
            const wrapper = shallow(<Offerers {...props} />)

            // then
            const offererItem = wrapper.find(PendingOffererItem)
            expect(offererItem).toHaveLength(1)
            expect(offererItem.at(0).prop('offerer')).toStrictEqual(offerer)
          })
        })

        describe('when the user does not have access', () => {
          it('should render a pending offerer item', () => {
            // given
            const offerer = {
              id: 'B2',
              siren: '1431',
              isValidated: true,
              userHasAccess: false,
            }
            props.offerers = [offerer]

            // when
            const wrapper = shallow(<Offerers {...props} />)

            // then
            const offererItem = wrapper.find(PendingOffererItem)
            expect(offererItem).toHaveLength(1)
            expect(offererItem.at(0).prop('offerer')).toStrictEqual(offerer)
          })
        })
      })
    })

    describe('the link to offerer creation page', () => {
      describe('when api sirene feature is available', () => {
        it('should display a link to create an offer', () => {
          // when
          const wrapper = shallow(<Offerers {...props} />)
          const pageHeading = wrapper.find(Titles).first().dive()

          const link = pageHeading.find(Link)

          // then
          expect(link.prop('to')).toBe('/structures/creation')
        })
      })

      describe('when api sirene feature is not available', () => {
        it('should display a link to unavailable page', () => {
          // given
          props.isOffererCreationAvailable = false

          // when
          const wrapper = shallow(<Offerers {...props} />)
          const pageHeading = wrapper.find(Titles).first().dive()

          const link = pageHeading.find(Link)

          // then
          expect(link.prop('to')).toBe('/erreur/indisponible')
        })
      })
    })
  })
})
