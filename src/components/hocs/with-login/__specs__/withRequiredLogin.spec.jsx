import { handleFail, handleSuccess } from '../withRequiredLogin'

describe('src | components | pages | hocs | with-login | withRequiredLogin - unit tests', () => {
  const state = {}

  describe('handleFail()', () => {
    describe('when authentication fails', () => {
      it('should redirect to signin with initial requested route as parameter', () => {
        // given
        const state = {}
        const action = {}
        const ownProps = {
          history: {
            push: jest.fn(),
          },
          location: {
            pathname: 'pathname',
            search: 'search',
          },
        }

        // when
        handleFail(state, action, ownProps)

        // then
        expect(ownProps.history.push).toHaveBeenCalledWith(`/connexion?de=pathnamesearch`)
      })
    })
  })

  describe('handleSuccess()', () => {
    describe('when authentication succeed', () => {
      describe('when user has completed cultural survey and seen tutorials', () => {
        it('should not redirect', () => {
          // given
          const action = {
            payload: {
              datum: {
                email: 'michel.marx@example.com',
                needsToFillCulturalSurvey: false,
                needsToSeeTutorials: false,
              },
            },
          }

          const ownProps = {
            history: {
              push: jest.fn(),
            },
            location: {
              pathname: '/test',
              search: '',
            },
          }

          // when
          handleSuccess(state, action, ownProps)

          // then
          expect(ownProps.history.push).not.toHaveBeenCalled()
        })
      })

      describe('when user has completed cultural survey and has not seen tutorials', () => {
        it('should redirect to tutorials', () => {
          // given
          const action = {
            payload: {
              datum: {
                email: 'michel.marx@example.com',
                needsToFillCulturalSurvey: false,
                needsToSeeTutorials: true,
              },
            },
          }

          const ownProps = {
            history: {
              push: jest.fn(),
            },
            location: {
              pathname: '/test',
              search: '',
            },
          }

          // when
          handleSuccess(state, action, ownProps)

          // then
          expect(ownProps.history.push).toHaveBeenCalledWith('/bienvenue')
        })
      })

      describe('when user has not completed cultural survey', () => {
        it('should redirect to cultural survey', () => {
          // given
          const action = {
            payload: {
              datum: {
                email: 'michel.marx@example.com',
                needsToFillCulturalSurvey: true,
              },
            },
          }

          const ownProps = {
            history: {
              push: jest.fn(),
            },
            location: {
              key: expect.any(String),
              pathname: '/test',
            },
          }

          // when
          handleSuccess(state, action, ownProps)

          // then
          expect(ownProps.history.push).toHaveBeenCalledWith('/typeform')
        })
      })
    })
  })
})
