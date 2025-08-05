import { api } from 'apiClient/api'
import { yupResolver } from '@hookform/resolvers/yup'
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as siretApiValidate from 'commons/core/Venue/siretApiValidate'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { FormProvider, useForm } from 'react-hook-form'
import { Button } from 'ui-kit/Button/Button'
import { expect, vi } from 'vitest'

import {
  SiretOrCommentFields,
  SiretOrCommentFieldsProps,
} from '../SiretOrCommentFields'
import { generateSiretValidationSchema } from '../validationSchema'

vi.mock('commons/core/Venue/siretApiValidate')

vi.mock('apiClient/api', () => ({
  api: {
    getSiretInfo: vi.fn(),
    getDataFromAddress: vi.fn(),
  },
}))

const onSubmit = vi.fn()

function renderSiretOrComment(
  defaultProps: SiretOrCommentFieldsProps,
  isSiretValued = true,
  options?: RenderWithProvidersOptions
) {
  const Wrapper = () => {
    const methods = useForm({
      defaultValues: { comment: '', siret: '' },
      resolver: yupResolver(
        generateSiretValidationSchema(false, isSiretValued, '012345678')
      ),
      mode: 'all',
    })

    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <SiretOrCommentFields {...defaultProps} />
          <Button type="submit" isLoading={false}>
            Enregistrer
          </Button>
        </form>
      </FormProvider>
    )
  }

  renderWithProviders(<Wrapper />, options)
}

describe('SiretOrCommentFields', () => {
  let props: SiretOrCommentFieldsProps

  beforeEach(() => {
    const setIsFieldNameFrozen = vi.fn()

    props = {
      setIsFieldNameFrozen: setIsFieldNameFrozen,
      siren: '123456789',
      initialSiret: '12345678901234',
    }
  })

  it('should display Siret when siret is provided', () => {
    renderSiretOrComment(props)

    const siretField = screen.getByLabelText('SIRET de la structure *')
    expect(siretField).toBeInTheDocument()
    const commentField = screen.queryByText(
      'Commentaire de la structure sans SIRET'
    )
    expect(commentField).not.toBeInTheDocument()
  })

  it('should display comment field when there is no siret', () => {
    renderSiretOrComment({
      ...props,
      initialSiret: '',
    })

    const siretField = screen.queryByText('SIRET de la structure')
    expect(siretField).not.toBeInTheDocument()
    const commentField = screen.getByLabelText(
      'Commentaire de la structure sans SIRET',
      {
        exact: false,
      }
    )
    expect(commentField).toBeInTheDocument()
  })

  describe('should validate SIRET on submit', () => {
    it('handles onSiretChange and calls APIs and form methods', async () => {
      vi.spyOn(api, 'getSiretInfo').mockResolvedValue({
        active: false,
        address: {
          city: '',
          postalCode: '',
          street: '',
        },
        ape_code: '',
        legal_category_code: '',
        name: '',
        siret: '',
      })

      renderSiretOrComment({ ...props })

      // Find input again after rerender
      const siretInput = screen.getByLabelText(/SIRET de la structure/i)

      // Simulate input change with a valid siret starting with siren
      await userEvent.type(siretInput, '12345678901234')

      await waitFor(() => {
        expect(api.getSiretInfo).toHaveBeenCalledWith('12345678901234')
      })
    })

    it('should submit valid form', async () => {
      renderSiretOrComment(props)

      const siretInput = screen.getByLabelText('SIRET de la structure', {
        exact: false,
      })
      await userEvent.type(siretInput, '01234567800000')
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )

      expect(onSubmit).toHaveBeenCalledTimes(1)
    })

    it('should display required message if siret is empty for non virtual venue', async () => {
      renderSiretOrComment(props)

      expect(
        screen.queryByText('Veuillez renseigner un SIRET ')
      ).not.toBeInTheDocument()
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )

      expect(
        await screen.findByText('Veuillez renseigner un SIRET')
      ).toBeInTheDocument()
    })

    it('should not display required message if siret is empty for virtual venue', async () => {
      renderSiretOrComment(props)

      expect(
        screen.queryByText('Veuillez renseigner un SIRET')
      ).not.toBeInTheDocument()
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )

      expect(
        await screen.findByText('Veuillez renseigner un SIRET')
      ).toBeInTheDocument()
    })

    it('user should not be able to enter non number characters', async () => {
      renderSiretOrComment(props)

      const siretInput: HTMLInputElement = screen.getByLabelText(
        'SIRET de la structure',
        {
          exact: false,
        }
      )

      await userEvent.type(siretInput, 'abc')

      expect(siretInput.value).toEqual('')
    })

    it('user should be able to enter number characters', async () => {
      renderSiretOrComment(props)

      const siretInput: HTMLInputElement = screen.getByLabelText(
        'SIRET de la structure',
        {
          exact: false,
        }
      )

      await userEvent.type(siretInput, '123')

      expect(siretInput.value).toEqual('123')
    })

    it('should display too short message if siret is not 14 characters if venue is non virtual', async () => {
      renderSiretOrComment(props)

      const siretInput = screen.getByLabelText('SIRET de la structure', {
        exact: false,
      })
      await userEvent.click(siretInput)
      await userEvent.type(siretInput, '12345')
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )

      const errorMessage = await screen.findByText(
        'Le SIRET doit comporter 14 caractères'
      )
      expect(errorMessage).toBeInTheDocument()
    })

    it('should display error message if siret does not match siren if venue is non virtual', async () => {
      renderSiretOrComment(props)

      const siretInput = screen.getByLabelText('SIRET de la structure', {
        exact: false,
      })
      await userEvent.click(siretInput)
      await userEvent.type(siretInput, '11122233344400')
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )

      const errorMessage = await screen.findByText(
        'Le code SIRET doit correspondre à un établissement de votre structure'
      )
      expect(errorMessage).toBeInTheDocument()
    })

    it('should call api validation and display error message if siret is not valid if venue is non virtual', async () => {
      vi.spyOn(siretApiValidate, 'siretApiValidate').mockResolvedValue(
        'Le code siret est invalide'
      )

      renderSiretOrComment(props)

      const siretInput = screen.getByLabelText('SIRET de la structure', {
        exact: false,
      })
      await userEvent.click(siretInput)
      await userEvent.type(siretInput, '01234567800000')
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )

      const errorMessage = await screen.findByText(
        'Le code SIRET saisi n’est pas valide'
      )
      expect(errorMessage).toBeInTheDocument()
    })
  })

  describe('should validate comment on submit', () => {
    it('should display error message if comment empty', async () => {
      renderSiretOrComment(
        {
          ...props,
          initialSiret: '',
        },
        false
      )

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )

      expect(
        screen.getByText('Veuillez renseigner un commentaire')
      ).toBeInTheDocument()
    })
  })
})
