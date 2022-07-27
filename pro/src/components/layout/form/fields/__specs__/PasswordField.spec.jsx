import '@testing-library/jest-dom'

import { fireEvent, render, screen } from '@testing-library/react'
import React from 'react'
import { Form } from 'react-final-form'

import PasswordField, { isNotValid } from '../PasswordField'

describe('component | PasswordField', () => {
  describe('isNotValid', () => {
    it('should return true when has no character', () => {
      const result = isNotValid('')

      expect(result).toStrictEqual(['Ce champ est obligatoire'])
    })

    it('should return false when has at least one character', () => {
      const result = isNotValid('une valeur')

      expect(result).toBeNull()
    })
  })

  describe('rendering', () => {
    let props = {
      label: 'labelTest',
      name: 'nameTest',
    }
    it('should display custom error message when backend error starts with "ton mot de passe"', () => {
      // Given
      render(
        <Form onSubmit={jest.fn}>
          {({ handleSubmit }) => (
            <form onSubmit={handleSubmit}>
              <PasswordField
                {...props}
                errors={['Ton mot de passe gloubi boulga']}
              />
            </form>
          )}
        </Form>
      )
      fireEvent.click(
        screen.getByRole('button', { name: 'Afficher le mot de passe' })
      )

      // When
      const input = screen.getByRole('textbox', {
        name: 'labelTest Cacher le mot de passe',
      })
      fireEvent.change(input, {
        target: { value: 'tutu' },
      })

      // Then
      expect(
        screen.getByText(
          'Votre mot de passe doit contenir au moins : - 12 caractères - Un chiffre - Une majuscule et une minuscule - Un caractère spécial'
        )
      ).toBeInTheDocument()
    })

    it('should display backned error message when backend error does not start with "ton mot de passe"', () => {
      // Given
      render(
        <Form onSubmit={jest.fn}>
          {({ handleSubmit }) => (
            <form onSubmit={handleSubmit}>
              <PasswordField {...props} errors={['An error']} />
            </form>
          )}
        </Form>
      )
      fireEvent.click(
        screen.getByRole('button', { name: 'Afficher le mot de passe' })
      )

      // When
      const input = screen.getByRole('textbox', {
        name: 'labelTest Cacher le mot de passe',
      })
      fireEvent.change(input, {
        target: { value: 'tutu' },
      })

      // Then
      expect(screen.getByText('An error')).toBeInTheDocument()
    })
  })
})
