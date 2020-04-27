import React from 'react'
import SignupForm from '../SignupForm'
import { shallow } from 'enzyme'
import { Field, Form, SubmitButton } from 'pass-culture-shared'
import { NavLink } from 'react-router-dom'

describe('src | components | pages | Signup | SignupForm', () => {
  let props

  beforeEach(() => {
    props = {
      errors: [],
      offererName: 'super structure',
      patch: {},
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<SignupForm {...props} />)

    // then
    expect(wrapper).toMatchSnapshot()
  })

  describe('render', () => {
    it('should render a disabled submit button when required inputs are not filled', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const submitButton = wrapper
        .find(SubmitButton)
        .dive()
        .find('button')
      expect(submitButton.prop('disabled')).toBe(true)
    })

    it('should render a Form component with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const form = wrapper.find(Form)
      expect(form).toHaveLength(1)
      expect(form.prop('action')).toBe('/users/signup/pro')
      expect(form.prop('BlockComponent')).toBeNull()
      expect(form.prop('formatPatch')).toStrictEqual(expect.any(Function))
      expect(form.prop('handleSuccessNotification')).toBeNull()
      expect(form.prop('handleSuccessRedirect')).toStrictEqual(expect.any(Function))
      expect(form.prop('layout')).toBe('vertical')
      expect(form.prop('name')).toBe('user')
      expect(form.prop('patch')).toStrictEqual({})
    })

    it('should render nine Field components', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const fields = wrapper.find(Field)
      expect(fields).toHaveLength(9)
    })

    it('should render a Field component for email with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const field = wrapper.find(Field).at(0)
      expect(field.prop('label')).toBe('Adresse e-mail')
      expect(field.prop('name')).toBe('email')
      expect(field.prop('placeholder')).toBe('nom@exemple.fr')
      expect(field.prop('required')).toBe(true)
      expect(field.prop('sublabel')).toBe(
        'pour se connecter et récupérer son mot de passe en cas d’oubli'
      )
      expect(field.prop('type')).toBe('email')
    })

    it('should render a Field component for password with the right props', () => {
      // given
      const infoContent = `
          <Fragment>Votre mot de passe doit contenir au moins :
            <ul>
              <li>12 caractères</li>
              <li>une majuscule et une minuscule</li>
              <li>un chiffre</li>
              <li>un caractère spécial (signe de ponctuation, symbole monétaire ou mathématique)</li>
            </ul>
          </Fragment>`

      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const field = wrapper.find(Field).at(1)
      expect(field.prop('info')).toBe(infoContent)
      expect(field.prop('label')).toBe('Mot de passe')
      expect(field.prop('name')).toBe('password')
      expect(field.prop('placeholder')).toBe('Mon mot de passe')
      expect(field.prop('required')).toBe(true)
      expect(field.prop('sublabel')).toBe('pour se connecter')
      expect(field.prop('type')).toBe('password')
    })

    it('should render a Field component for lastname with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const field = wrapper.find(Field).at(2)
      expect(field.prop('label')).toBe('Nom')
      expect(field.prop('name')).toBe('lastName')
      expect(field.prop('placeholder')).toBe('Mon nom')
      expect(field.prop('required')).toBe(true)
    })

    it('should render a Field component for firstname with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const field = wrapper.find(Field).at(3)
      expect(field.prop('label')).toBe('Prénom')
      expect(field.prop('name')).toBe('firstName')
      expect(field.prop('placeholder')).toBe('Mon prénom')
      expect(field.prop('required')).toBe(true)
    })

    it('should render a Field component for phone number with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const field = wrapper.find(Field).at(4)
      expect(field.prop('label')).toBe('Téléphone')
      expect(field.prop('name')).toBe('phoneNumber')
      expect(field.prop('placeholder')).toBe('Mon numéro de téléphone')
      expect(field.prop('sublabel')).toBe("utilisé uniquement par l'équipe du pass Culture")
      expect(field.prop('required')).toBe(true)
    })

    it('should render a Field component for siren with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const field = wrapper.find(Field).at(5)
      expect(field.prop('disabling')).toStrictEqual(expect.any(Function))
      expect(field.prop('label')).toBe('SIREN')
      expect(field.prop('name')).toBe('siren')
      expect(field.prop('placeholder')).toBe('123 456 789')
      expect(field.prop('required')).toBe(true)
      expect(field.prop('sublabel')).toBe('de la structure que vous représentez')
      expect(field.prop('type')).toBe('siren')
      expect(field.prop('withFetchedName')).toBe(true)
    })

    it('should render a Field component for newsletter agreement with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const field = wrapper.find(Field).at(6)
      expect(field.prop('label')).toBe('Je souhaite recevoir les actualités du pass Culture')
      expect(field.prop('name')).toBe('newsletter_ok')
      expect(field.prop('type')).toBe('checkbox')
    })

    it('should render a Field component for contact agreement with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const field = wrapper.find(Field).at(7)
      expect(field.prop('label')).toBe(
        "J’accepte d'être contacté par e-mail pour donner mon avis sur le pass Culture"
      )
      expect(field.prop('name')).toBe('contact_ok')
      expect(field.prop('required')).toBe(true)
      expect(field.prop('type')).toBe('checkbox')
    })

    it('should render a Field component for cgu agreement with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const field = wrapper.find(Field).at(8)
      expect(field.prop('label')).toStrictEqual(
        <React.Fragment>
          {'J’ai lu et j’accepte les '}
          <a
            href="https://docs.passculture.app/textes-normatifs"
            id="accept-cgu-link"
            rel="noopener noreferrer"
            target="_blank"
          >
            {'Conditions Générales d’Utilisation'}
          </a>
        </React.Fragment>
      )
      expect(field.prop('name')).toBe('cgu_ok')
      expect(field.prop('required')).toBe(true)
      expect(field.prop('type')).toBe('checkbox')
    })

    it('should render errors when provided', () => {
      // given
      props.errors = ['error1']

      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const errors = wrapper.find('.errors')
      expect(errors.text()).toBe('error1')
    })

    it('should render a NavLink component with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const navLink = wrapper.find(NavLink)
      expect(navLink).toHaveLength(1)
      expect(navLink.prop('className')).toBe('button is-secondary')
      expect(navLink.prop('to')).toBe('/connexion')
    })

    it('should render a SubmitButton component with the right props', () => {
      // when
      const wrapper = shallow(<SignupForm {...props} />)

      // then
      const submitButton = wrapper.find(SubmitButton)
      expect(submitButton).toHaveLength(1)
      expect(submitButton.prop('className')).toBe('button is-primary is-outlined')
      expect(submitButton.prop('type')).toBe('submit')
      expect(submitButton.dive().text()).toBe('Créer')
    })
  })

})
