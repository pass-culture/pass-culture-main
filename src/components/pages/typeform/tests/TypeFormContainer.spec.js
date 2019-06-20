import uuid from 'uuid/v1'

import * as config from '../../../../utils/config'
import { mapStateToProps } from '../TypeFormContainer'

jest.mock('uuid/v1')

describe('src | components |pages | typeform | TypeFormContainer', () => {
  it('should return empty object when current user is not defined', () => {
    // given
    config.TYPEFORM_URL_CULTURAL_PRACTICES_POLL = 'mocked_typeform_uri'
    uuid.mockImplementation(() => 'mocked_uuid')
    const state = { data: { users: [] } }

    // when
    const result = mapStateToProps(state)

    // then
    const expected = {
      needsToFillCulturalSurvey: undefined,
      typeformUrl: `mocked_typeform_uri?userId=mocked_uuid`,
      uniqId: 'mocked_uuid',
    }
    expect(result).toStrictEqual(expected)
  })

  it('should return an url with search parameters: currentUser.id', () => {
    // given
    config.TYPEFORM_URL_CULTURAL_PRACTICES_POLL = 'mocked_typeform_uri'
    uuid.mockImplementation(() => 'mocked_uuid')
    const state = {
      data: {
        users: [
          {
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
      typeformUrl: `mocked_typeform_uri?userId=mocked_uuid`,
      uniqId: 'mocked_uuid',
    }
    expect(result).toStrictEqual(expected)
  })
})
