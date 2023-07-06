import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Form } from 'react-final-form'

import * as getSirenDataAdapter from 'core/Offerers/adapters/getSirenDataAdapter'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffererCreationForm from '../OffererCreationForm'

describe('src | components | pages | OffererCreationForm', () => {
  const renderOffererCreationForm = () =>
    renderWithProviders(
      <Form
        backTo="/accueil"
        onSubmit={() => {}}
        // @ts-expect-error FIXME: migrate component to formik
        component={OffererCreationForm}
      />
    )

  it('should be clickable when values have been changed and are valid', async () => {
    // given
    jest.spyOn(getSirenDataAdapter, 'default').mockResolvedValue({
      isOk: true,
      message: '',
      payload: {
        values: {
          address: '4 rue du test',
          city: 'Plessix-Balisson',
          name: 'Ma Petite structure',
          postalCode: '22350',
          siren: '881457238',
          apeCode: '',
        },
      },
    })

    // When
    renderOffererCreationForm()
    const input = screen.getByRole('textbox')
    await userEvent.type(input, '123456789')
    await userEvent.tab()

    // Then
    expect(screen.getByRole('button')).not.toHaveAttribute('disabled')
  })

  it('should not be clickable when form is invalid', async () => {
    jest.spyOn(getSirenDataAdapter, 'default').mockResolvedValue({
      isOk: false,
      message: 'SIREN trop long',
      payload: {},
    })

    // When
    renderOffererCreationForm()
    const input = screen.getByRole('textbox')
    await userEvent.type(input, '12345678981723')

    // Then
    expect(screen.getByRole('button')).toHaveAttribute('disabled')
  })

  it('should not be clickable when values have not been changed', () => {
    // given

    // When
    renderOffererCreationForm()

    // Then
    expect(screen.getByRole('button')).toHaveAttribute('disabled')
  })
})
