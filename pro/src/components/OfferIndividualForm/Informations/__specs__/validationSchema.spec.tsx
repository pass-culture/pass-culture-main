import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { OfferIndividualFormValues } from 'components/OfferIndividualForm'
import { SubmitButton } from 'ui-kit'

import Informations, { InformationsProps } from '../Informations'
import { validationSchema } from '../validationSchema'

const renderInformations = async ({
  props,
  initialValues,
  onSubmit = vi.fn(),
}: {
  props: InformationsProps
  initialValues: Partial<OfferIndividualFormValues>
  onSubmit: () => void
}) => {
  const rtlReturns = render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Form>
        <Informations {...props} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )

  return {
    ...rtlReturns,
    buttonSubmit: screen.getByRole('button', {
      name: 'Submit',
    }),
  }
}

describe('OfferIndividual section: UsefulInformations', () => {
  let initialValues: Partial<OfferIndividualFormValues>
  const onSubmit = vi.fn()
  let props: InformationsProps

  beforeEach(() => {
    initialValues = {
      subCategoryFields: [
        'author',
        'ean',
        'performer',
        'speaker',
        'stageDirector',
        'visa',
        'durationMinutes',
      ],
      name: '',
      description: '',
      author: '',
      ean: '',
      performer: '',
      speaker: '',
      stageDirector: '',
      visa: '',
      durationMinutes: '',
    }

    props = {
      readOnlyFields: [],
    }
  })

  it('should submit valid form', async () => {
    const { buttonSubmit } = await renderInformations({
      props,
      initialValues,
      onSubmit,
    })
    const nameInput = screen.getByLabelText('Titre de l’offre', {
      exact: false,
    })
    await userEvent.type(nameInput, 'Mon super titre')

    await userEvent.click(buttonSubmit)

    expect(onSubmit).toHaveBeenCalledWith(
      {
        author: '',
        description: '',
        durationMinutes: '',
        name: 'Mon super titre',
        performer: '',
        speaker: '',
        stageDirector: '',
        subCategoryFields: [
          'author',
          'ean',
          'performer',
          'speaker',
          'stageDirector',
          'visa',
          'durationMinutes',
        ],
        ean: '',
        visa: '',
      },
      expect.anything()
    )
  })

  it('should display errors for mandatory fields', async () => {
    const { buttonSubmit } = await renderInformations({
      props,
      initialValues,
      onSubmit,
    })
    const nameInput = screen.getByLabelText('Titre de l’offre', {
      exact: false,
    })
    await userEvent.click(nameInput)
    await userEvent.tab()
    await userEvent.click(buttonSubmit)
    expect(
      await screen.findByText('Veuillez renseigner un titre')
    ).toBeInTheDocument()

    expect(screen.queryByTestId('error-author')).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-ean')).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-performer')).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-speaker')).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-stageDirector')).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-visa')).not.toBeInTheDocument()
    expect(
      screen.queryByTestId('error-durationMinutes')
    ).not.toBeInTheDocument()
  })

  describe('test durationMinutes errors', () => {
    const durationMinutesValidDataSet = ['1:00', '10:04', '320:00', '12:12']
    it.each(durationMinutesValidDataSet)(
      'test valid format (durationMinutes ="%s")',
      async durationMinutesValue => {
        initialValues.subCategoryFields = ['durationMinutes']
        const { buttonSubmit } = await renderInformations({
          props,
          initialValues,
          onSubmit,
        })

        const durationMinutesInput = screen.getByLabelText('Durée', {
          exact: false,
        })
        await userEvent.type(durationMinutesInput, durationMinutesValue)
        await userEvent.click(buttonSubmit)
        expect(
          screen.queryByTestId('error-durationMinutes')
        ).not.toBeInTheDocument()
      }
    )
  })
})
