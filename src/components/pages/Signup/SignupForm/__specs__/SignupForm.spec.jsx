import React from 'react'
import SignupForm from '../SignupForm'
import { mount } from 'enzyme'
import { NavLink } from 'react-router-dom'
import { createBrowserHistory } from 'history'
import { Router } from 'react-router'

describe('src | components | pages | Signup | SignupForm', () => {
  let props
  let history

  beforeEach(() => {
    props = {
      closeNotification: jest.fn(),
      createNewProUser: jest.fn(),
      errors: [],
      redirectToConfirmation: jest.fn(),
      showNotification: jest.fn(),
    }

    history = createBrowserHistory()
  })

  describe('render', () => {
    it('should render a disabled submit button when required inputs are not filled', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.prop('disabled')).toBe(true)
    })

    it('should render nine Field components', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const fields = wrapper.find('label')
      expect(fields).toHaveLength(9)
    })

    it('should render a Field component for email with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(0)
      expect(field.text()).toBe(
        'Adresse e-mail*...pour se connecter et récupérer son mot de passe en cas d’oubli'
      )
      const input = field.find('input')
      expect(input.prop('name')).toBe('email')
      expect(input.prop('placeholder')).toBe('nom@exemple.fr')
      expect(input.prop('type')).toBe('text')
    })

    it('should render a Field component for password with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(1)
      expect(field.text()).toBe('Mot de passe*...pour se connecter ')
      const input = field.find('input')
      expect(input.prop('name')).toBe('password')
      expect(input.prop('placeholder')).toBe('Mon mot de passe')
      expect(input.prop('type')).toBe('password')
    })

    it('should render a Field component for lastname with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(2)
      expect(field.text()).toBe('Nom*')
      const input = field.find('input')
      expect(input.prop('name')).toBe('lastName')
      expect(input.prop('placeholder')).toBe('Mon nom')
    })

    it('should render a Field component for firstname with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(3)
      expect(field.text()).toBe('Prénom*')
      const input = field.find('input')
      expect(input.prop('name')).toBe('firstName')
      expect(input.prop('placeholder')).toBe('Mon prénom')
    })

    it('should render a Field component for phone number with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(4)
      expect(field.text()).toBe('Téléphone*...utilisé uniquement par l’équipe du pass Culture')
      const input = field.find('input')
      expect(input.prop('name')).toBe('phoneNumber')
      expect(input.prop('placeholder')).toBe('Mon numéro de téléphone')
    })

    it('should render a Field component for siren with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(5)
      expect(field.text()).toBe('SIREN*... de la structure que vous représentez')
      const input = field.find('input')
      expect(input.prop('name')).toBe('siren')
      expect(input.prop('placeholder')).toBe('123 456 789')
      expect(input.prop('type')).toBe('text')
    })

    it('should render a Field component for newsletter agreement with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(6)
      expect(field.text()).toBe('Je souhaite recevoir les actualités du pass Culture')
      const input = field.find('input')
      expect(input.prop('name')).toBe('newsletter_ok')
      expect(input.prop('type')).toBe('checkbox')
    })

    it('should render a Field component for contact agreement with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(7)
      expect(field.text()).toBe(
        'J’accepte d’être contacté par e-mail pour donner mon avis sur le pass Culture*'
      )
      const input = field.find('input')
      expect(input.prop('name')).toBe('contact_ok')
      expect(input.prop('type')).toBe('checkbox')
    })

    it('should render a Field component for cgu agreement with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(8)
      expect(field.text()).toStrictEqual(
        'J’ai lu et j’accepte les Conditions Générales d’Utilisation*'
      )
      const input = field.find('input')
      expect(input.prop('name')).toBe('cgu_ok')
      expect(input.prop('type')).toBe('checkbox')
    })

    it('should render errors when provided', () => {
      // given
      props.errors = { email: 'erreur sur le mail' }

      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const errors = wrapper.find('.field-error-message')
      expect(errors.text()).toBe('erreur sur le mail')
    })

    it('should render a NavLink component with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const navLink = wrapper.find(NavLink)
      expect(navLink).toHaveLength(1)
      expect(navLink.prop('className')).toBe('button is-secondary')
      expect(navLink.prop('to')).toBe('/connexion')
    })

    it('should render a SubmitButton component with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton).toHaveLength(1)
      expect(submitButton.prop('className')).toBe('button is-primary')
      expect(submitButton.prop('type')).toBe('submit')
      expect(submitButton.text()).toBe('Créer')
    })
  })
})
