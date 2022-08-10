import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm/types'
import { SubmitButton } from 'ui-kit'

import Informations, { IInformationsProps } from '../Informations'
import { validationSchema } from '../validationSchema'

const renderInformations = async ({
  props,
  initialValues,
  onSubmit = jest.fn(),
}: {
  props: IInformationsProps
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
}) => {
  const rtlReturns = await render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <Informations {...props} />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
        </form>
      )}
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
  let initialValues: Partial<IOfferIndividualFormValues>
  const onSubmit = jest.fn()
  let props: IInformationsProps

  beforeEach(() => {
    initialValues = {
      subCategoryFields: [
        'author',
        'isbn',
        'performer',
        'speaker',
        'stageDirector',
        'visa',
        'durationMinutes',
      ],
      name: '',
      description: '',
      author: '',
      isbn: '',
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

  it('should display errors for mandatory fields', async () => {
    const { buttonSubmit } = await renderInformations({
      props,
      initialValues,
      onSubmit,
    })
    const nameInput = screen.getByLabelText("Titre de l'offre", {
      exact: false,
    })
    await userEvent.click(nameInput)
    await userEvent.tab()
    await userEvent.click(buttonSubmit)
    expect(
      await screen.findByText('Veuillez renseigner un titre')
    ).toBeInTheDocument()

    expect(screen.queryByTestId('error-author')).not.toBeInTheDocument()
    expect(screen.queryByTestId('error-isbn')).not.toBeInTheDocument()
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
          await screen.queryByText(
            'Veuillez entrer une durée sous la forme HH:MM (ex: 1:30 pour 1h30)'
          )
        ).not.toBeInTheDocument()
      }
    )

    const durationMinutesFormatErrorDataSet = [
      'ABCD',
      '-1:40',
      '12:120',
      '12:AB',
      'AB:CD',
    ]
    it.each(durationMinutesFormatErrorDataSet)(
      'testing format error (durationMinutes="%s")',
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
          await screen.findByText(
            'Veuillez entrer une durée sous la forme HH:MM (ex: 1:30 pour 1h30)'
          )
        ).toBeInTheDocument()
      }
    )
    it('should not allow more than 59 minutes', async () => {
      initialValues.subCategoryFields = ['durationMinutes']
      const { buttonSubmit } = await renderInformations({
        props,
        initialValues,
        onSubmit,
      })

      const durationMinutesInput = screen.getByLabelText('Durée', {
        exact: false,
      })
      await userEvent.type(durationMinutesInput, '12:60')
      await userEvent.click(buttonSubmit)
      expect(
        await screen.findByText(
          'Une heure ne peut pas avoir plus de 59 minutes'
        )
      ).toBeInTheDocument()
    })
  })
})
