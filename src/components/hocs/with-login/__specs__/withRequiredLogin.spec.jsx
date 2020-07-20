import { handleFail, handleSuccess } from '../withRequiredLogin'

describe('src | components | pages | hocs | with-login | withRequiredLogin - unit tests', () => {
  describe('handleFail()', () => {
    describe('when authentication fails', () => {
      it('should redirect to signin with initial requested route as parameter', () => {
        // given
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
        handleFail(ownProps)

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
          const user = {
            email: 'michel.marx@example.com',
            needsToFillCulturalSurvey: false,
            needsToSeeTutorials: false,
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
          handleSuccess(user, ownProps)

          // then
          expect(ownProps.history.push).not.toHaveBeenCalled()
        })
      })

      describe('when user has completed cultural survey and has not seen tutorials', () => {
        it('should redirect to tutorials', () => {
          // given
          const user = {
            email: 'michel.marx@example.com',
            needsToSeeTutorials: true,
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
          handleSuccess(user, ownProps)

          // then
          expect(ownProps.history.push).toHaveBeenCalledWith('/bienvenue')
        })
      })

      describe('when user has not completed cultural survey', () => {
        it('should redirect to cultural survey', () => {
          // given
          const user = {
            email: 'michel.marx@example.com',
            needsToFillCulturalSurvey: true,
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
          handleSuccess(user, ownProps)

          // then
          expect(ownProps.history.push).toHaveBeenCalledWith('/typeform')
        })
      })
    })
  })
})
