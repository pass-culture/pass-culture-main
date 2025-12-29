import { yupResolver } from '@hookform/resolvers/yup'
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { expect, vi } from 'vitest'

import { getSiretData } from '@/commons/core/Venue/getSiretData'
import { structureDataBodyModelFactory } from '@/commons/utils/factories/userOfferersFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { Button } from '@/ui-kit/Button/Button'

import {
  SiretOrCommentFields,
  type SiretOrCommentFieldsProps,
} from '../SiretOrCommentFields'
import { SiretOrCommentValidationSchema } from '../validationSchema'

vi.mock('@/commons/core/Venue/siretApiValidate')

vi.mock('@/commons/core/Venue/getSiretData', () => ({
  getSiretData: vi.fn(),
}))

const onSubmit = vi.fn()

const defaultFormContext: SiretOrCommentFieldsProps['formContext'] = {
  isCaledonian: false,
  withSiret: true,
  isVenueVirtual: false,
  siren: '123456789',
}

const defaultInitialValues = {
  comment: '',
  siret: '12345678901234',
}

function renderSiretOrComment(
  defaultProps: SiretOrCommentFieldsProps,
  initalValues?: { comment: string; siret: string },
  options?: RenderWithProvidersOptions
) {
  const Wrapper = () => {
    const methods = useForm({
      context: {
        ...defaultFormContext,
        ...defaultProps.formContext,
      },
      defaultValues: {
        ...defaultInitialValues,
        ...(initalValues || {}),
      },
      resolver: yupResolver(SiretOrCommentValidationSchema),
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
      setIsFieldNameFrozen,
      formContext: defaultFormContext,
    }
  })

  it('should display Siret when siret is provided', () => {
    renderSiretOrComment(props)

    const siretField = screen.getByLabelText(/SIRET de la structure/)
    expect(siretField).toBeInTheDocument()
    const commentField = screen.queryByText(
      'Commentaire de la structure sans SIRET'
    )
    expect(commentField).not.toBeInTheDocument()
  })

  it('should display comment field when there is no siret', () => {
    renderSiretOrComment({
      ...props,
      formContext: {
        ...props.formContext,
        withSiret: false,
      },
    })

    const siretField = screen.queryByText(/SIRET de la structure/)
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
      vi.mocked(getSiretData)
        .mockResolvedValueOnce(structureDataBodyModelFactory())
        .mockRejectedValueOnce(
          new Error('Impossible de vérifier le SIRET saisi.')
        )

      renderSiretOrComment(props)

      // Find input again after rerender
      const siretInput = screen.getByLabelText(/SIRET de la structure/i)

      // Simulate input change with a valid siret starting with siren
      await userEvent.clear(siretInput)
      await userEvent.type(siretInput, '123 456 789 01234')

      await waitFor(() => {
        expect(getSiretData).toHaveBeenCalledWith('123 456 789 01234')
      })

      await waitFor(() =>
        expect(props.setIsFieldNameFrozen).toHaveBeenCalledWith(true)
      )

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )

      await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1))
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'ma super stucture',
          addressAutocomplete: '4 rue Carnot 75001 Paris',
          street: '4 rue Carnot',
          postalCode: '75001',
          city: 'Paris',
          latitude: '48.869440910282734',
          longitude: '2.3087717501609233',
          inseeCode: '75056',
        }),
        expect.anything()
      )

      await userEvent.clear(siretInput)
      await userEvent.type(siretInput, '123 456 789 01235')

      await waitFor(() => {
        expect(getSiretData).toHaveBeenCalledWith('123 456 789 01235')
      })

      expect(
        await screen.findByText('Impossible de vérifier le SIRET saisi.')
      ).toBeInTheDocument()
    })

    it('handles onRidetChange and unhumanize value', async () => {
      renderSiretOrComment({
        ...props,
        formContext: {
          ...defaultFormContext,
          isCaledonian: true,
          siren: '1234567',
        },
      })

      const ridetInput: HTMLInputElement = screen.getByLabelText(
        /RIDET de la structure/
      )
      await userEvent.clear(ridetInput)
      await userEvent.type(ridetInput, '1234567890')

      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )

      await waitFor(() => expect(onSubmit).toHaveBeenCalled())
      expect(props.setIsFieldNameFrozen).toHaveBeenCalledWith(false)
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          siret: '1234567890',
          comment: '',
        }),
        expect.anything()
      )
    })

    it('should display error if siret is not diffusible', async () => {
      vi.mocked(getSiretData).mockResolvedValue({
        ...structureDataBodyModelFactory(),
        name: 'Siret is not diffusible',
        isDiffusible: false,
      })

      renderSiretOrComment(props)

      // Find input again after rerender
      const siretInput = screen.getByLabelText(/SIRET de la structure/i)

      // Simulate input change with a valid siret starting with siren
      await userEvent.clear(siretInput)
      await userEvent.type(siretInput, '123 456 789 01235')

      await waitFor(() => {
        expect(getSiretData).toHaveBeenCalledWith('123 456 789 01235')
      })

      expect(
        await screen.findByText(
          'Certaines informations de votre structure ne sont pas diffusibles. Veuillez contacter le support.'
        )
      ).toBeInTheDocument()
    })

    it('should submit valid form', async () => {
      renderSiretOrComment(props)

      const siretInput = screen.getByLabelText('SIRET de la structure', {
        exact: false,
      })
      await userEvent.clear(siretInput)
      await userEvent.type(siretInput, '12345678900000')
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
      const siretInput = screen.getByLabelText('SIRET de la structure', {
        exact: false,
      })
      await userEvent.clear(siretInput)
      await userEvent.tab()
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
      renderSiretOrComment(props, {
        ...defaultInitialValues,
        siret: '',
      })

      expect(
        screen.queryByText('Veuillez renseigner un SIRET')
      ).not.toBeInTheDocument()
      await userEvent.click(
        screen.getByRole('button', {
          name: 'Enregistrer',
        })
      )
    })

    it('user should not be able to enter non number characters', async () => {
      renderSiretOrComment(props)

      const siretInput: HTMLInputElement = screen.getByLabelText(
        'SIRET de la structure',
        {
          exact: false,
        }
      )

      await userEvent.clear(siretInput)
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

      await userEvent.clear(siretInput)
      await userEvent.type(siretInput, '123')

      expect(siretInput.value).toEqual('123')
    })

    it('should display too short message if siret is not 14 characters if venue is non virtual', async () => {
      renderSiretOrComment(props)

      const siretInput = screen.getByLabelText('SIRET de la structure', {
        exact: false,
      })
      await userEvent.click(siretInput)
      await userEvent.clear(siretInput)
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
      await userEvent.clear(siretInput)
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
  })

  describe('should validate comment on submit', () => {
    it('should display error message if comment empty', async () => {
      const commentFormContext: SiretOrCommentFieldsProps['formContext'] = {
        ...defaultFormContext,
        withSiret: false,
        isVenueVirtual: true,
      }
      renderSiretOrComment(
        {
          ...props,
          formContext: commentFormContext,
        },
        {
          ...defaultInitialValues,
          siret: '',
        }
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
