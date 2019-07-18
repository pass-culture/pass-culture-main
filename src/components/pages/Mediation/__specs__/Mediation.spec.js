import { shallow } from 'enzyme'
import React from 'react'
import Mediation from '../Mediation'

describe('src | components | pages | Mediation', () => {
  let props

  beforeEach(() => {
    props = {
      match: {
        params: {
          offerId: 'AGKA',
        },
      },
      mediation: {},
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<Mediation {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })
})
