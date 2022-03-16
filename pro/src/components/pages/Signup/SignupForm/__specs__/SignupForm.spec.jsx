import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'
import { Link } from 'react-router-dom'

import SignupForm from '../SignupForm'

describe('src | components | pages | Signup | SignupForm', () => {
  let props
  let history

  beforeEach(() => {
    props = {
      createNewProUser: jest.fn(),
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
      const signUpFormTitle = wrapper.find({
        children: 'Créer votre compte professionnel',
      })
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
        children:
          'Merci de compléter les champs suivants pour créer votre compte.',
      })
      expect(signUpFormSubTitle).toHaveLength(1)
    })

    it('should display an external link to the help center', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const helpCenterLink = wrapper
        .find({ children: 'Consulter notre centre d’aide' })
        .parent('a')
      expect(helpCenterLink).toHaveLength(1)
      expect(helpCenterLink.prop('href')).toBe(
        'https://passculture.zendesk.com/hc/fr/articles/4411999179665'
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
      const cguLink = wrapper
        .find({ children: 'Conditions Générales d’Utilisation' })
        .parent('a')
      expect(cguLink).toHaveLength(1)
      expect(cguLink.prop('href')).toBe(
        'https://pass.culture.fr/cgu-professionnels/'
      )
    })

    it('should display an external link to GDPR chart', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const gdprLink = wrapper
        .find({ children: 'Charte des Données Personnelles' })
        .parent('a')
      expect(gdprLink).toHaveLength(1)
      expect(gdprLink.prop('href')).toBe(
        'https://pass.culture.fr/donnees-personnelles/'
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
      const mailToSupportLink = wrapper
        .find({ children: 'contactez notre support.' })
        .parent('a')
      expect(mailToSupportLink).toHaveLength(1)
      expect(mailToSupportLink.prop('href')).toBe(
        'mailto:support-pro@passculture.app'
      )
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
      expect(field.text()).toBe('Adresse e-mail')
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
      expect(field.text()).toBe('Mot de passe')
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
      expect(field.text()).toBe('Nom')
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
      expect(field.text()).toBe('Prénom')
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
      expect(field.text()).toBe(
        'Téléphone (utilisé uniquement par l’équipe du pass Culture)'
      )
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
      expect(field.text()).toBe('SIREN de la structure que vous représentez')
      const input = field.find('input')
      expect(input.prop('name')).toBe('siren')
      expect(input.prop('placeholder')).toBe('123456789')
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
        'J’accepte d’être contacté par e-mail pour recevoir les nouveautés du pass Culture et contribuer à son amélioration (facultatif)'
      )
      const input = field.find('input')
      expect(input.prop('name')).toBe('contactOk')
      expect(input.prop('type')).toBe('checkbox')
    })

    it('should render a Link component', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const link = wrapper.find(Link)
      expect(link).toHaveLength(1)
      expect(link.prop('to')).toBe('/connexion')
    })

    it('should render a link to RGS information', () => {
      // when
      const wrapper = mount(
        <Router history={history}>
          <SignupForm {...props} />
        </Router>
      )

      // then
      const RGSLink = wrapper.find('a').at(4)
      expect(RGSLink.prop('href')).toBe(
        'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-'
      )
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
      expect(submitButton.prop('type')).toBe('submit')
      expect(submitButton.text()).toBe('Créer mon compte')
    })
  })
})
