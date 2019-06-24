import { currentUserUUID } from 'with-react-redux-login'

import { mapStateToProps } from '../TypeFormContainer'

describe('src | components |pages | typeform | TypeFormContainer', () => {
  it('should return empty object when current user is not defined', () => {
    // given
    const state = { data: { users: [] } }

    // when
    const result = mapStateToProps(state)

    // then
    const expected = {
      needsToFillCulturalSurvey: undefined,
    }
    expect(result).toStrictEqual(expected)
  })

  it('should return an url with search parameters: currentUser.id', () => {
    // given
    const state = {
      data: {
        users: [
          {
            currentUserUUID,
            needsToFillCulturalSurvey: true,
          },
        ],
      },
    }

    // when
    const result = mapStateToProps(state)

    // then
    const expected = {
      needsToFillCulturalSurvey: true,
    }
    expect(result).toStrictEqual(expected)
  })
})
