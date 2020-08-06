import { shallow } from 'enzyme'
import React from 'react'
import { Form } from 'react-final-form'

import TextField from '../../../layout/form/fields/TextField'
import Titles from '../../../layout/Titles/Titles'
import Profil from '../Profil'

describe('src | components | pages | Profil', () => {
  let dispatch
  let props

  beforeEach(() => {
    dispatch = jest.fn()
    props = {
      currentUser: {
        email: 'fake email',
        publicName: 'fake publicName',
      },
      dispatch,
    }
  })

  it('should render a Titles component with right properties', () => {
    // when
    const wrapper = shallow(<Profil {...props} />)

    // then
    const titlesComponent = wrapper.find(Titles)
    expect(titlesComponent).toHaveLength(1)
    expect(titlesComponent.prop('title')).toBe('Profil')
  })

  it('should render three TextField components with the right properties', () => {
    // when
    const wrapper = shallow(<Profil {...props} />)

    // then
    const form = wrapper.find(Form).dive()
    const textFieldComponents = form.find(TextField)
    expect(textFieldComponents).toHaveLength(2)
    expect(textFieldComponents.at(0).prop('name')).toBe('publicName')
    expect(textFieldComponents.at(0).prop('label')).toBe('Nom :')
    expect(textFieldComponents.at(0).prop('placeholder')).toBe('3 caractères minimum')
    expect(textFieldComponents.at(0).prop('required')).toBe(true)
    expect(textFieldComponents.at(1).prop('name')).toBe('email')
    expect(textFieldComponents.at(1).prop('label')).toBe('E-mail :')
    expect(textFieldComponents.at(1).prop('required')).toBe(true)
  })

  it('should update user informations successfully when submitting form', () => {
    // given
    const wrapper = shallow(<Profil {...props} />)
    const formComponent = wrapper.find(Form).dive()
    const innerForm = formComponent.find('form')

    // when
    innerForm.simulate('submit')

    // then
    expect(dispatch.mock.calls[0][0]).toStrictEqual({
      config: {
        apiPath: '/users/current',
        body: {
          email: 'fake email',
          publicName: 'fake publicName',
        },
        handleFail: expect.any(Function),
        handleSuccess: expect.any(Function),
        isMergingDatum: true,
        method: 'PATCH',
      },
      type: 'REQUEST_DATA_PATCH_/USERS/CURRENT',
    })
    expect(wrapper.state('isLoading')).toBe(true)
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
