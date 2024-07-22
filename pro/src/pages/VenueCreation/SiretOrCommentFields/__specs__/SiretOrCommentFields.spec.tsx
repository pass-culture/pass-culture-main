import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import * as siretApiValidate from 'core/Venue/siretApiValidate'
import { VenueCreationFormValues } from 'pages/VenueCreation/types'
import { VenueEditionFormValues } from 'pages/VenueEdition/types'
import { Button } from 'ui-kit/Button/Button'

import {
  SiretOrCommentFields,
  SiretOrCommentFieldsProps,
} from '../SiretOrCommentFields'
import { generateSiretValidationSchema } from '../validationSchema'

vi.mock('core/Venue/siretApiValidate')

vi.mock('apiClient/api', () => ({
  api: {
    getSiretInfo: vi.fn(),
    getDataFromAddress: vi.fn(),
  },
}))

const renderSiretOrComment = async ({
  initialValues,
  onSubmit = vi.fn(),
  props,
  validationSchema,
}: {
  initialValues: Partial<VenueEditionFormValues>
  onSubmit: () => void
  props: SiretOrCommentFieldsProps
  validationSchema: any
}) => {
  const rtlReturns = render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <SiretOrCommentFields {...props} />
          <Button type="submit" isLoading={false}>
            Submit
          </Button>
        </form>
      )}
    </Formik>
  )

  return {
    ...rtlReturns,
    buttonSubmit: await waitFor(() =>
      screen.getByRole('button', {
        name: 'Submit',
      })
    ),
  }
}

describe('components | SiretOrCommentFields', () => {
  let props: SiretOrCommentFieldsProps
  let initialValues: Partial<VenueCreationFormValues>
  let validationSchema: any
  const onSubmit = vi.fn()

  beforeEach(() => {
    const setIsFieldNameFrozen = vi.fn()
    const updateIsSiretValued = vi.fn()
    validationSchema = generateSiretValidationSchema(false, true, '012345678')
    initialValues = { comment: '', siret: '' }
    props = {
      isCreatedEntity: true,
      setIsFieldNameFrozen: setIsFieldNameFrozen,
      updateIsSiretValued: updateIsSiretValued,
      siren: '123456789',
    }
  })

  it('should display Siret by default', async () => {
    await renderSiretOrComment({
      initialValues,
      onSubmit,
      props,
      validationSchema,
    })
    const siretField = screen.getByLabelText('SIRET du lieu *')
    expect(siretField).toBeInTheDocument()
    const commentField = screen.queryByText('Commentaire du lieu sans SIRET')
    expect(commentField).not.toBeInTheDocument()
  })

  it('should display comment field when toggle is clicked', async () => {
    await renderSiretOrComment({
      initialValues,
      onSubmit,
      props,
      validationSchema,
    })

    const toggle = screen.getByRole('button', {
      name: 'Ce lieu possède un SIRET',
    })
    await userEvent.click(toggle)
    const siretField = screen.queryByText('SIRET du lieu')
    expect(siretField).not.toBeInTheDocument()
    const commentField = screen.getByLabelText(
      'Commentaire du lieu sans SIRET',
      {
        exact: false,
      }
    )
    expect(commentField).toBeInTheDocument()
  })

  it('should display toggle disabled', async () => {
    props.isToggleDisabled = true
    await renderSiretOrComment({
      initialValues,
      onSubmit,
      props,
      validationSchema,
    })

    const toggle = screen.getByRole('button', {
      name: 'Ce lieu possède un SIRET',
    })
    expect(toggle).toBeDisabled()
  })

  describe('should validate SIRET on submit', () => {
    it('should submit valid form', async () => {
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })

      const siretInput = screen.getByLabelText('SIRET du lieu', {
        exact: false,
      })
      await userEvent.type(siretInput, '01234567800000')
      await userEvent.click(buttonSubmit)

      expect(onSubmit).toHaveBeenCalledTimes(1)
    })
    it('should display required message if siret is empty for non virtual venue', async () => {
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })

      expect(
        screen.queryByText('Veuillez renseigner un SIRET')
      ).not.toBeInTheDocument()
      await userEvent.click(buttonSubmit)

      expect(
        await screen.findByText('Veuillez renseigner un SIRET')
      ).toBeInTheDocument()
    })

    it('should not display required message if siret is empty for virtual venue', async () => {
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })

      expect(
        screen.queryByText('Veuillez renseigner un SIRET')
      ).not.toBeInTheDocument()
      await userEvent.click(buttonSubmit)

      expect(
        await screen.findByText('Veuillez renseigner un SIRET')
      ).toBeInTheDocument()
    })
    it('user should not be able to enter non number characters', async () => {
      await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })

      const siretInput: HTMLInputElement = screen.getByLabelText(
        'SIRET du lieu',
        {
          exact: false,
        }
      )

      await userEvent.type(siretInput, 'abc')

      expect(siretInput.value).toEqual('')
    })
    it('user should be able to enter number characters', async () => {
      await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })

      const siretInput: HTMLInputElement = screen.getByLabelText(
        'SIRET du lieu',
        {
          exact: false,
        }
      )

      await userEvent.type(siretInput, '123')

      expect(siretInput.value).toEqual('123')
    })
    it('should display too short message if siret is not 14 characters if venue is non virtual', async () => {
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })

      const siretInput = screen.getByLabelText('SIRET du lieu', {
        exact: false,
      })
      await userEvent.click(siretInput)
      await userEvent.type(siretInput, '12345')
      await userEvent.click(buttonSubmit)

      const errorMessage = await screen.findByText(
        'Le SIRET doit comporter 14 caractères'
      )
      expect(errorMessage).toBeInTheDocument()
    })
    it('should display error message if siret does not match siren if venue is non virtual', async () => {
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })

      const siretInput = screen.getByLabelText('SIRET du lieu', {
        exact: false,
      })
      await userEvent.click(siretInput)
      await userEvent.type(siretInput, '11122233344400')
      await userEvent.click(buttonSubmit)

      const errorMessage = await screen.findByText(
        'Le code SIRET doit correspondre à un établissement de votre structure'
      )
      expect(errorMessage).toBeInTheDocument()
    })
    it('should call api validation and display error message if siret is not valid if venue is non virtual', async () => {
      vi.spyOn(siretApiValidate, 'siretApiValidate').mockResolvedValue(
        'Le code siret est invalide'
      )
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })
      const siretInput = screen.getByLabelText('SIRET du lieu', {
        exact: false,
      })
      await userEvent.click(siretInput)
      await userEvent.type(siretInput, '01234567800000')
      await userEvent.click(buttonSubmit)

      const errorMessage = await screen.findByText(
        'Le code SIRET saisi n’est pas valide'
      )
      expect(errorMessage).toBeInTheDocument()
    })
  })
  describe('should validate comment on submit', () => {
    it('should display error message if comment empty', async () => {
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema: generateSiretValidationSchema(false, false, null),
      })

      const toggle = screen.getByRole('button', {
        name: 'Ce lieu possède un SIRET',
      })
      await userEvent.click(toggle)
      await userEvent.click(buttonSubmit)

      expect(
        screen.getByText('Veuillez renseigner un commentaire')
      ).toBeInTheDocument()
    })
  })
})
