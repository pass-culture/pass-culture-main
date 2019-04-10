import { mapDispatchToProps } from '../BlockContainer'
import { closeModal } from 'pass-culture-shared'

describe('src | components | layout | BlockContainer', () => {
  describe('mapDispatchToProps', () => {
    let dispatch
    beforeEach(() => {
      dispatch = jest.fn()
    })

    describe('onConfirmation', () => {
      it('should unblock navigation', () => {
        // given
        const unblock = jest.fn()
        const ownProps = {
          unblock,
          nextLocation: { pathname: '/offres', search: '?venueId=D4' },
          history: { push: jest.fn() },
        }

        // when
        mapDispatchToProps(dispatch, ownProps).onConfirmation()

        // then
        expect(unblock).toHaveBeenCalled()
      })

      it('should redirect to nextLocation', () => {
        // given
        const unblock = jest.fn()
        const ownProps = {
          unblock,
          nextLocation: { pathname: '/offres', search: '?venueId=D4' },
          history: { push: jest.fn() },
        }

        // when
        mapDispatchToProps(dispatch, ownProps).onConfirmation()

        // then
        expect(ownProps.history.push).toHaveBeenCalledWith('/offres?venueId=D4')
      })

      it('should close modal', () => {
        // given
        const unblock = jest.fn()
        const ownProps = {
          unblock,
          nextLocation: { pathname: '/offres', search: '?venueId=D4' },
          history: { push: jest.fn() },
        }

        // when
        mapDispatchToProps(dispatch, ownProps).onConfirmation()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          keepComponentMounted: undefined,
          type: 'CLOSE_MODAL',
        })
      })
    })

    describe('onCancel', () => {
      it('should close modal', () => {
        // given
        const ownProps = {}

        // when
        mapDispatchToProps(dispatch, ownProps).onCancel()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          keepComponentMounted: undefined,
          type: 'CLOSE_MODAL',
        })
      })
    })
  })
})
