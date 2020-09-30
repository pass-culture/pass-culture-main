import { shallow } from 'enzyme'
import React from 'react'

import Profil from '../Profil'
import { MemoryRouter } from 'react-router'
import configureStore from '../../../../utils/store'
import { Provider } from 'react-redux'
import { render, screen, fireEvent } from '@testing-library/react'

describe('src | components | pages | Profil', () => {
  let dispatch
  let props
  let store

  const renderProfil = props =>
    render(
      <Provider store={store}>
        <MemoryRouter>
          <Profil {...props} />
        </MemoryRouter>
      </Provider>
    )

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
    renderProfil(props)

    // then
    expect(screen.getByRole('heading', { name: 'Profil' })).not.toBeNull()
  })

  it('should render two inputs for name and email address', () => {
    // when
    renderProfil(props)

    // then
    expect(screen.getByLabelText('Nom :')).not.toBeNull()
    expect(screen.getByLabelText('E-mail :')).not.toBeNull()
  })

  it('should update user informations successfully when submitting form', () => {
    // given
    renderProfil(props)

    // when
    const submitButton = screen.getByText('Enregistrer')
    fireEvent.click(submitButton)

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
    renderProfil(props)
    fireEvent.click(screen.getByText('Enregistrer'))

    // then
    expect(dispatch).not.toHaveBeenCalled()
  })

  it('should disable submit button when name input value is under 3 characters', () => {
    // given
    renderProfil(props)
    const input = screen.getByLabelText('Nom :')
    fireEvent.change(input, { target: { value: 'AA' } })

    // when
    fireEvent.click(screen.getByText('Enregistrer'))

    // then
    expect(dispatch).not.toHaveBeenCalled()
  })

  it('should display an error message on submit if email format is not valid', () => {
    // given
    renderProfil(props)
    const inputEmail = screen.getByLabelText('E-mail :')
    fireEvent.change(inputEmail, { target: { value: 'fake@email' } })

    // when
    fireEvent.click(screen.getByText('Enregistrer'))

    // then
    expect(screen.getByText('Le format de l’email est incorrect.')).not.toBeNull()
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
