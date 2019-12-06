import React from 'react'
import { shallow } from 'enzyme'
import { MemoryRouter } from 'react-router-dom'
import { createBrowserHistory } from 'history'

import Typeform from '../Typeform'

const history = createBrowserHistory()
history.push('/typeform')

describe('src | components | pages | typeform | Typeform', () => {
  it('should match the snapshots with required props', () => {
    // given
    const props = {
      flagUserHasFilledTypeform: jest.fn(),
      needsToFillCulturalSurvey: true,
    }

    // when
    const wrapper = shallow(
      <MemoryRouter
        initialEntries={['/typeform']}
        keyLength={0}
      >
        <Typeform {...props} />
      </MemoryRouter>
    )

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
