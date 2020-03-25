import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import Loader from '../Loader'

describe('layout | Loader', () => {
  let props

  beforeEach(() => {
    props = {
      hasError: false,
      isEmpty: false,
      isLoading: false,
      match: {
        params: {
          mediationId: 'MEFA',
        },
      },
      statusCode: 200,
    }
  })

  it('should display error message when status code is 500', () => {
    // given
    const history = createBrowserHistory()
    props.hasError = true
    props.statusCode = 500

    // when
    const wrapper = mount(
      <Router history={history}>
        <Loader {...props} />
      </Router>
    )

    // then
    const wording = wrapper.find({
      children: 'Une erreur s’est produite pendant le chargement du carrousel.',
    })
    expect(wording).toHaveLength(1)
  })
})
