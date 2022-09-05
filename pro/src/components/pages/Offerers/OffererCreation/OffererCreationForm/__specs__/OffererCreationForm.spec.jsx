import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Form } from 'react-final-form'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import * as getSirenDataAdapter from 'core/Offerers/adapters/getSirenDataAdapter'
import { configureTestStore } from 'store/testUtils'

import OffererCreationForm from '../OffererCreationForm'

describe('src | components | pages | OffererCreationForm', () => {
  const renderOffererCreationForm = () => {
    const store = configureTestStore()
    return render(
      <Provider store={store}>
        <MemoryRouter>
          <Form onSubmit={() => {}} component={OffererCreationForm} />
        </MemoryRouter>
      </Provider>
    )
  }

  it('should be clickable when values have been changed and are valid', async () => {
    // given
    jest.spyOn(getSirenDataAdapter, 'default').mockResolvedValue({
      isOk: true,
      message: '',
      payload: {
        values: {
          address: '4 rue du test',
          city: 'Plessix-Balisson',
          latitude: 1.1,
          longitude: 1.1,
          name: 'Ma Petite structure',
          postalCode: '22350',
          siren: '881457238',
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
    // given

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
