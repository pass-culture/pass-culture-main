import React from 'react'
import { shallow } from 'enzyme'

import Offerers from '../Offerers'
import OffererItemContainer from '../OffererItem/OffererItemContainer'
import PendingOffererItem from '../OffererItem/PendingOffererItem'

describe('src | components | pages | Offerers | Offerers', () => {
  let props

  beforeEach(() => {
    props = {
      closeNotification: jest.fn(),
      currentUser: {},
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

  it('should match the snapshot', () => {
    // when
    const wrapper = shallow(<Offerers {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    describe('subtitle message', () => {
      it('should display a link to create an offer', () => {
        // when
        const wrapper = shallow(<Offerers {...props} />)
        const links = wrapper.find('a')

        // then
        expect(links.at(0).text()).toBe('créer un nouveau lieu ')
        expect(links.at(0).prop('href')).toBe('/structures/AE/lieux/creation')
      })

      it('should display a link to create a venue', () => {
        // when
        const wrapper = shallow(<Offerers {...props} />)
        const links = wrapper.find('a')

        // then
        expect(links.at(1).text()).toBe('ajouter des offres numériques.')
        expect(links.at(1).prop('href')).toBe('/offres/creation')
      })
    })

    describe('should pluralize offerers menu link', () => {
      it('should display Votre structure when one offerer', () => {
        // given
        props.currentUser = {}
        props.offerers = [{ id: 'AE' }]

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const titles = wrapper.find('Titles').props()

        // then
        expect(titles.title).toStrictEqual('Votre structure juridique')
      })

      it('should display Vos structures when many offerers', () => {
        // given
        props.currentUser = {}
        props.offerers = [{ id: 'AE' }, { id: 'AF' }]

        // when
        const wrapper = shallow(<Offerers {...props} />)
        const titles = wrapper.find('Titles').props()

        // then
        expect(titles.title).toStrictEqual('Vos structures juridiques')
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

      it('should close offerer notifcation', () => {
        // given
        props = {
          ...props,
          closeNotification: jest.fn(),
          notification: {
            tag: 'offerers',
          },
        }
        const wrapper = shallow(<Offerers {...props} />)

        // when
        wrapper.unmount()

        // then
        expect(props.closeNotification).toHaveBeenCalledWith()
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
            const offerer = { id: 'B2', siren: '1431', isValidated: false, userHasAccess: true }
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
            const offerer = { id: 'B2', siren: '1431', isValidated: true, userHasAccess: false }
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
  })
})
