import React from 'react'
import { shallow } from 'enzyme'
import { MemoryRouter } from 'react-router-dom'
import { createBrowserHistory } from 'history'

import TypeForm from '../TypeForm'

const history = createBrowserHistory()
history.push('/typeform')

describe('src | components | pages | typeform | TypeForm', () => {
  it('should match snapshots with required props', () => {
    // given
    const props = {
      flagUserHasFilledTypeform: jest.fn(),
      needsToFillCulturalSurvey: true,
    }

    // when
    const wrapper = shallow(
      <MemoryRouter initialEntries={['/typeform']} keyLength={0}>
        <TypeForm {...props} />
      </MemoryRouter>
    )

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
