import '@testing-library/jest-dom'

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import * as siretApiValidate from 'components/layout/form/fields/SiretField/validators/siretApiValidate'
import { IVenueFormValues } from 'new_components/VenueForm'
import { SubmitButton } from 'ui-kit'

import SiretOrCommentFields, {
  SiretOrCommentInterface,
} from '../SiretOrCommentFields'
import generateSiretValidationSchema from '../validationSchema'

jest.mock(
  'components/layout/form/fields/SiretField/validators/siretApiValidate'
)

jest.mock('apiClient/api', () => ({
  api: {
    getSiretInfo: jest.fn(),
    getDataFromAddress: jest.fn(),
  },
}))

const renderSiretOrComment = async ({
  initialValues,
  onSubmit = jest.fn(),
  props,
  validationSchema,
}: {
  initialValues: Partial<IVenueFormValues>
  onSubmit: () => void
  props: SiretOrCommentInterface
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
          <SubmitButton isLoading={false}>Submit</SubmitButton>
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
  let props: SiretOrCommentInterface
  let initialValues: Partial<IVenueFormValues>
  let validationSchema: any
  const onSubmit = jest.fn()

  beforeEach(() => {
    const siretLabel = 'Siret field'
    const setIsFieldNameFrozen = jest.fn()
    const updateIsSiretValued = jest.fn()
    validationSchema = generateSiretValidationSchema('012345678', true)
    initialValues = { comment: '', siret: '' }
    props = {
      isCreatedEntity: true,
      setIsFieldNameFrozen: setIsFieldNameFrozen,
      siretLabel: siretLabel,
      readOnly: false,
      updateIsSiretValued: updateIsSiretValued,
    }
  })

  it('should display siret field by default', async () => {
    await renderSiretOrComment({
      initialValues,
      onSubmit,
      props,
      validationSchema,
    })
    const siretField = screen.getByLabelText('Siret field')
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
      name: 'Je veux créer un lieu avec SIRET',
    })
    await userEvent.click(toggle)
    const siretField = screen.queryByText('Siret field')
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
      name: 'Je veux créer un lieu avec SIRET',
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

      const siretInput = screen.getByLabelText('Siret field', {
        exact: false,
      })
      await userEvent.type(siretInput, '01234567800000')
      await userEvent.click(buttonSubmit)

      expect(onSubmit).toHaveBeenCalledTimes(1)
    })
    it('should display required message if siret is empty', async () => {
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
        'Siret field',
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
        'Siret field',
        {
          exact: false,
        }
      )

      await userEvent.type(siretInput, '123')

      expect(siretInput.value).toEqual('123')
    })
    it('should display too short message if siret is not 14 characters', async () => {
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })

      const siretInput = screen.getByLabelText('Siret field', {
        exact: false,
      })
      await userEvent.click(siretInput)
      await userEvent.type(siretInput, '12345')
      await userEvent.click(buttonSubmit)

      const errorMessage = await screen.findByText(
        'Le SIRET doit comporter 14 charactères'
      )
      expect(errorMessage).toBeInTheDocument()
    })
    it('should display error message if siret does not match siren', async () => {
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })

      const siretInput = screen.getByLabelText('Siret field', {
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
    it('should call api validation and display error message if siret is not valid', async () => {
      jest
        .spyOn(siretApiValidate, 'default')
        .mockResolvedValue('Le code siret est invalide')
      const { buttonSubmit } = await renderSiretOrComment({
        initialValues,
        onSubmit,
        props,
        validationSchema,
      })
      const siretInput = screen.getByLabelText('Siret field', {
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
})
