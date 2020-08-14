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
      errors: {},
      redirectToConfirmation: jest.fn(),
      showNotification: jest.fn(),
    }

    history = createBrowserHistory()
  })

  describe('render', () => {
    it('should display the title "Créer votre compte professionnel"', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const signUpFormTitle = wrapper.find({ children: 'Créer votre compte professionnel' })
      expect(signUpFormTitle).toHaveLength(1)
    })

    it('should display a subtitle', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const signUpFormSubTitle = wrapper.find({
        children: 'Merci de compléter les champs suivants pour créer votre compte.',
      })
      expect(signUpFormSubTitle).toHaveLength(1)
    })

    it('should display an external link to the presentation of Pass Culture Pro', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const presentationLink = wrapper
        .find({ children: 'Fonctionnement du pass Culture pro' })
        .parent('a')
      expect(presentationLink).toHaveLength(1)
      expect(presentationLink.prop('href')).toBe(
        'https://docs.passculture.app/le-pass-culture-en-quelques-mots'
      )
    })

    it('should display an external link to the help center', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const helpCenterLink = wrapper.find({ children: 'Consulter notre centre d’aide' }).parent('a')
      expect(helpCenterLink).toHaveLength(1)
      expect(helpCenterLink.prop('href')).toBe(
        'https://aide.passculture.app/fr/article/acteurs-creer-un-compte-professionnel-t0m1hj/'
      )
    })

    it('should display an external link to CGU', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const cguLink = wrapper.find({ children: 'Conditions Générales d’Utilisation' }).parent('a')
      expect(cguLink).toHaveLength(1)
      expect(cguLink.prop('href')).toBe('https://docs.passculture.app/textes-normatifs')
    })

    it('should display an external link to GDPR chart', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const gdprLink = wrapper.find({ children: 'Charte des Données Personnelles' }).parent('a')
      expect(gdprLink).toHaveLength(1)
      expect(gdprLink.prop('href')).toBe(
        'https://docs.passculture.app/textes-normatifs/charte-des-donnees-personnelles'
      )
    })

    it('should display a mail to support', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const mailToSupportLink = wrapper.find({ children: 'contactez notre support.' }).parent('a')
      expect(mailToSupportLink).toHaveLength(1)
      expect(mailToSupportLink.prop('href')).toBe('mailto:support@passculture.app')
    })

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

    it('should render seven Field components', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const fields = wrapper.find('label')
      expect(fields).toHaveLength(7)
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

    it('should render a Field component for contact agreement with the right props', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const field = wrapper.find('label').at(6)
      expect(field.text()).toBe(
        'J’accepte d’être contacté par e-mail pour donner mon avis sur le pass Culture*'
      )
      const input = field.find('input')
      expect(input.prop('name')).toBe('contact_ok')
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
      expect(navLink.prop('className')).toBe('secondary-button')
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
      expect(submitButton.prop('className')).toBe('primary-button')
      expect(submitButton.prop('type')).toBe('submit')
      expect(submitButton.text()).toBe('Créer mon compte')
    })
  })
})
