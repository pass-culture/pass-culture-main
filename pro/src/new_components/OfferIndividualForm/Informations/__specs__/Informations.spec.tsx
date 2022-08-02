import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm/types'

import Informations from '../Informations'
import { validationSchema } from '../validationSchema'

const renderInformations = ({
  initialValues,
  onSubmit = jest.fn(),
}: {
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Informations />
    </Formik>
  )
}

describe('OfferIndividual section: UsefulInformations', () => {
  let initialValues: Partial<IOfferIndividualFormValues>
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = {
      subCategoryFields: [],
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
  })

  it('should render non sub categories fields', async () => {
    await renderInformations({ initialValues, onSubmit })
    expect(screen.getByLabelText("Titre de l'offre")).toBeInTheDocument()
    expect(
      screen.getByLabelText('Description', { exact: false })
    ).toBeInTheDocument()

    expect(
      screen.queryByLabelText('Auteur', { exact: false })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('ISBN', { exact: false })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Intervenant', { exact: false })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Visa d’exploitation', { exact: false })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Metteur en scène', { exact: false })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Interprète', { exact: false })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('Durée', { exact: false })
    ).not.toBeInTheDocument()
  })

  it('should also render sub categories fields', async () => {
    initialValues.subCategoryFields = [
      'author',
      'isbn',
      'performer',
      'speaker',
      'stageDirector',
      'visa',
      'durationMinutes',
    ]
    await renderInformations({ initialValues, onSubmit })
    expect(screen.getByLabelText("Titre de l'offre")).toBeInTheDocument()
    expect(
      screen.getByLabelText('Description', { exact: false })
    ).toBeInTheDocument()

    expect(
      screen.queryByLabelText('Auteur', { exact: false })
    ).toBeInTheDocument()
    expect(screen.getByLabelText('ISBN', { exact: false })).toBeInTheDocument()
    expect(
      screen.getByLabelText('Intervenant', { exact: false })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('Visa d’exploitation', { exact: false })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('Metteur en scène', { exact: false })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('Interprète', { exact: false })
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Durée', { exact: false })).toBeInTheDocument()
  })
})
