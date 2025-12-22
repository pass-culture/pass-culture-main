import { yupResolver } from '@hookform/resolvers/yup'
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { expect, vi } from 'vitest'

import { api } from '@/apiClient/api'
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

vi.mock('@/apiClient/api', () => ({
  api: {
    getStructureData: vi.fn(),
    getDataFromAddress: vi.fn(),
  },
}))

const onSubmit = vi.fn()

const defaultFormContext: SiretOrCommentFieldsProps['formContext'] = {
  isCaledonian: false,
  withSiret: true,
  isVenueVirtual: false,
  siren: '123456789',
  isVenueActivityFeatureActive: false,
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
      setIsFieldNameFrozen: setIsFieldNameFrozen,
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
      vi.spyOn(api, 'getStructureData').mockResolvedValue(
        structureDataBodyModelFactory()
      )

      renderSiretOrComment(props)

      // Find input again after rerender
      const siretInput = screen.getByLabelText(/SIRET de la structure/i)

      // Simulate input change with a valid siret starting with siren
      await userEvent.clear(siretInput)
      await userEvent.type(siretInput, '12345678901234')

      await waitFor(() => {
        expect(api.getStructureData).toHaveBeenCalledWith('12345678901234')
      })
    })

    it('should display error if siret is not diffusible', async () => {
      vi.spyOn(api, 'getStructureData').mockResolvedValue({
        ...structureDataBodyModelFactory(),
        name: 'Siret is not diffusible',
        isDiffusible: false,
      })

      renderSiretOrComment(props)

      // Find input again after rerender
      const siretInput = screen.getByLabelText(/SIRET de la structure/i)

      // Simulate input change with a valid siret starting with siren
      await userEvent.clear(siretInput)
      await userEvent.type(siretInput, '12345678901235')

      await waitFor(() => {
        expect(api.getStructureData).toHaveBeenCalledWith('12345678901235')
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
