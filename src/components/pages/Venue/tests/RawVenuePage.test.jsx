import React from 'react'
import RawVenuePage from '../RawVenuePage'
import { shallow } from 'enzyme'

const dispatchMock = jest.fn()
describe('src | components | pages | Venue | RawVenuePage', () => {
  describe('snapshot', () => {
    it('should match snapshot', () => {
      // given
      const props = {
        currentUser: {},
        dispatch: dispatchMock,
        formComment: null,
        formLatitude: 5.15981,
        formLongitude: -52.63452,
        formSiret: '22222222411111',
        history: {},
        location: {
          search: '',
        },
        match: {
          params: {
            offererId: 'APEQ',
            venueId: 'AQYQ',
          },
        },
        name: 'Maison de la Brique',
        offerer: {},
        user: {},
        venuePatch: {},
      }

      // when
      const wrapper = shallow(<RawVenuePage {...props} />)

      // then
      expect(wrapper).toBeDefined()
      expect(wrapper).toMatchSnapshot()
    })
  })
  describe('render', () => {
    describe('when editing form', () => {
      it('should permit user to change the e-mail', () => {
        // given
        const props = {
          currentUser: {},
          dispatch: dispatchMock,
          formComment: null,
          formLatitude: 5.15981,
          formLongitude: -52.63452,
          formSiret: '22222222411111',
          history: {},
          location: {
            search: '?modifie',
          },
          match: {
            params: {
              offererId: 'APEQ',
              venueId: 'AQYQ',
            },
          },
          name: 'Maison de la Brique',
          offerer: {},
          user: {},
          venuePatch: {},
        }

        // when
        const wrapper = shallow(<RawVenuePage {...props} />)
        const expected = {
          isEdit: true,
          isLoading: false,
          isNew: false,
          isReadOnly: false,
        }

        // then
        expect(wrapper.state().isReadOnly).toEqual(expected.isReadOnly)
      })
    })
  })
  describe('functions', () => {
    describe('handleSuccess', () => {
      describe('When patching a Venue', () => {
        // given
        const pushMock = jest.fn()
        const props = {
          currentUser: {},
          dispatch: dispatchMock,
          formComment: null,
          formLatitude: 5.15981,
          formLongitude: -52.63452,
          formSiret: '22222222411111',
          history: {
            location: {
              pathname: '/fake',
            },
            push: pushMock,
          },
          location: {
            search: '',
          },
          match: {
            params: {
              offererId: 'APEQ',
              venueId: 'AQYQ',
            },
          },
          name: 'Maison de la Brique',
          offerer: {
            id: 'BQ',
          },
          user: {},
          venuePatch: {},
        }
        const action = {
          data: {
            bookingEmail: 'fake@email.com',
            id: 'CM',
          },
          method: 'PATCH',
          path: 'venues/CM',
          type: 'SUCCESS_DATA_PATCH_VENUES/CM',
        }

        it('should change pathname', () => {
          // // When
          const wrapper = shallow(<RawVenuePage {...props} />)
          wrapper.instance().handleSuccess(wrapper.state(), action)

          // Then
          expect(pushMock).toHaveBeenCalledWith('/structures/BQ/lieux/CM')
        })

        it('should dispatch a success message', () => {
          // When
          const wrapper = shallow(<RawVenuePage {...props} />)
          wrapper.instance().handleSuccess(wrapper.state(), action)

          const expected = {
            patch: {
              text: 'Lieu modifié avec succès !',
              type: 'success',
            },
            type: 'SHOW_NOTIFICATION',
          }

          // then
          expect(dispatchMock).toHaveBeenCalledWith(expected)
        })
      })
    })
  })
})
