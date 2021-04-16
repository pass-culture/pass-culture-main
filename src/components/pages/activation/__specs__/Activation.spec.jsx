import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getStubStore } from '../../../../utils/stubStore'
import Activation from '../Activation'

describe('activation', () => {
  it('should render route for activating password when token and email are given', () => {
    // when
    const mockStore = getStubStore({
      token: (
        state = {
          hasBeenChecked: false,
        }
      ) => state,
    })
    const wrapper = mount(
      <Provider store={mockStore}>
        <MemoryRouter
          initialEntries={[
            '/activation/A98Aq5IB-ttPPhsZaMX0aKuEJGjpv-_47vIezkegpM4?email=beneficiary@example.com',
          ]}
        >
          <Activation />
        </MemoryRouter>
      </Provider>
    )

    // then
    const title = wrapper.find({ children: 'Pour commencer, choisis ton mot de passe.' })
    expect(title).toHaveLength(1)
  })

  it('should render error component when wrong route is given', () => {
    // given
    const wrapper = mount(
      <MemoryRouter initialEntries={['/activation/error']}>
        <Activation />
      </MemoryRouter>
    )

    // then
    const title = wrapper.find({ children: 'Il semblerait que le lien cliqué soit incorrect.' })
    expect(title).toHaveLength(1)
  })

  it('should render InvalidLink component when route is exactly /activation/lien-invalide', () => {
    // given
    const wrapper = mount(
      <MemoryRouter initialEntries={['/activation/lien-invalide']}>
        <Activation />
      </MemoryRouter>
    )

    // then
    const title = wrapper.find({ children: 'Le lien sur lequel tu as cliqué est invalide.' })
    expect(title).toHaveLength(1)
  })
})
