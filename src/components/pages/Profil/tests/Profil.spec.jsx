import { shallow, mount } from 'enzyme'
import React from 'react'

import Titles from '../../../layout/Titles/Titles'
import Profil from '../Profil'
import { MemoryRouter } from 'react-router'
import configureStore from '../../../../utils/store'
import { Provider } from 'react-redux'

describe('src | components | pages | Profil', () => {
  let dispatch
  let props
  let store

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      currentUser: {
        email: 'fake@exemple.com',
        publicName: 'fake publicName',
      },
      dispatch,
    }
    store = configureStore({
      data: {
        users: [{ id: 'CMOI', publicName: 'user' }],
        offerers: [],
      },
    }).store
  })

  it('should render a Titles component with right properties', () => {
    // when
    const wrapper = shallow(<Profil {...props} />)

    // then
    const titlesComponent = wrapper.find(Titles)
    expect(titlesComponent).toHaveLength(1)
    expect(titlesComponent.prop('title')).toBe('Profil')
  })

  it('should render two inputs for name and email address', () => {
    // when
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Profil {...props} />
        </MemoryRouter>
      </Provider>
    )

    // then
    const inputName = wrapper.findWhere(node => node.text() === 'Nom :').first()
    const inputEmail = wrapper.findWhere(node => node.text() === 'E-mail :').first()
    expect(inputName).toHaveLength(1)
    expect(inputEmail).toHaveLength(1)
  })

  it('should update user informations successfully when submitting form', () => {
    // given
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Profil {...props} />
        </MemoryRouter>
      </Provider>
    )
    const submitButton = wrapper.find('form')

    // when
    submitButton.invoke('onSubmit')({ preventDefault: jest.fn() })

    // then
    expect(dispatch.mock.calls[0][0]).toStrictEqual({
      config: {
        apiPath: '/users/current',
        body: {
          email: 'fake@exemple.com',
          publicName: 'fake publicName',
        },
        handleFail: expect.any(Function),
        handleSuccess: expect.any(Function),
        isMergingDatum: true,
        method: 'PATCH',
      },
      type: 'REQUEST_DATA_PATCH_/USERS/CURRENT',
    })
  })

  it('should disable submit button when email input value is empty', () => {
    // given
    props.currentUser.email = ''
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Profil {...props} />
        </MemoryRouter>
      </Provider>
    )
    const submitButton = wrapper.find({ children: 'Enregistrer' })

    // then
    expect(submitButton.prop('disabled')).toBe(true)
  })

  it('should disable submit button when name input value is under 3 characters', () => {
    // given
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Profil {...props} />
        </MemoryRouter>
      </Provider>
    )
    const inputName = wrapper.findWhere(node => node.text() === 'Nom :').first()

    // when
    inputName.invoke('onChange')({ target: { value: 'AA' } })
    const submitButton = wrapper.find({ children: 'Enregistrer' })

    // then
    expect(submitButton.prop('disabled')).toBe(true)
  })

  it('should display an error message on submit if email format is not valid', () => {
    // given
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Profil {...props} />
        </MemoryRouter>
      </Provider>
    )
    const inputEmail = wrapper.findWhere(node => node.text() === 'E-mail :').first()

    // when
    inputEmail.invoke('onChange')({ target: { value: 'fake@email' } })
    wrapper.find('form').invoke('onSubmit')({ preventDefault: jest.fn() })
    const errorMessage = wrapper
      .findWhere(node => node.text() === 'Le format de l’email est incorrect.')
      .first()

    // then
    expect(errorMessage).toHaveLength(1)
  })

  describe('functions', () => {
    describe('handleSuccess', () => {
      it('should dispatch a show notification action with success message and set isLoading from state to false', () => {
        // given
        const wrapper = shallow(<Profil {...props} />)

        // when
        wrapper.instance().handleSuccess()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: {
            text: 'Informations mises à jour avec succès.',
            type: 'success',
          },
          type: 'SHOW_NOTIFICATION',
        })
        expect(wrapper.state('isLoading')).toBe(false)
      })
    })

    describe('handleFail', () => {
      it('should dispatch a show notification action with error message and set isLoading from state to false', () => {
        // given
        const wrapper = shallow(<Profil {...props} />)

        // when
        wrapper.instance().handleFail()

        // then
        expect(dispatch).toHaveBeenCalledWith({
          patch: {
            text: 'Erreur lors de la mise à jour de vos informations.',
            type: 'fail',
          },
          type: 'SHOW_NOTIFICATION',
        })
        expect(wrapper.state('isLoading')).toBe(false)
      })
    })
  })
})
