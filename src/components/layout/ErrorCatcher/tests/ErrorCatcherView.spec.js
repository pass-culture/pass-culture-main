/* eslint
  react/jsx-one-expression-per-line: 0 */
// jest --env=jsdom ./src/components/layout/error-catcher/tests/ErrorCatcherView --watch
import React from 'react'
import { shallow } from 'enzyme'
import ErrorCatcherView from '../ErrorCatcherView'

describe('src | components | layout | ErrorCatcher | ErrorCatcherView', () => {
  it('match snapshot', () => {
    // given
    const props = { onClick: jest.fn() }

    // when
    const wrapper = shallow(<ErrorCatcherView {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })
})
