import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { IOfferIndividualFormValues } from 'components/OfferIndividualForm/types'

import Informations, { IInformationsProps } from '../Informations'
import { validationSchema } from '../validationSchema'

const renderInformations = ({
  props,
  initialValues,
  onSubmit = jest.fn(),
}: {
  props: IInformationsProps
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Informations {...props} />
    </Formik>
  )
}

describe('OfferIndividual section: UsefulInformations', () => {
  let initialValues: Partial<IOfferIndividualFormValues>
  const onSubmit = jest.fn()
  let props: IInformationsProps

  beforeEach(() => {
    initialValues = {
      subCategoryFields: [],
      name: '',
      description: '',
      author: '',
      performer: '',
      speaker: '',
      stageDirector: '',
      visa: '',
      durationMinutes: '',
    }

    props = {}
  })

  it('should render non sub categories fields', async () => {
    renderInformations({ props, initialValues, onSubmit })
    expect(screen.getByLabelText('Titre de l’offre')).toBeInTheDocument()
    expect(
      screen.getByLabelText('Description', { exact: false })
    ).toBeInTheDocument()

    expect(
      screen.queryByLabelText('Auteur', { exact: false })
    ).not.toBeInTheDocument()
    expect(
      screen.queryByLabelText('EAN', { exact: false })
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
      'ean',
      'performer',
      'speaker',
      'stageDirector',
      'visa',
      'durationMinutes',
    ]
    renderInformations({ props, initialValues, onSubmit })
    expect(screen.getByLabelText(/Titre de l’offre/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Titre de l’offre/)).not.toBeDisabled()
    expect(screen.getByLabelText(/Description/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Description/)).not.toBeDisabled()
    expect(screen.getByLabelText(/Auteur/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Auteur/)).not.toBeDisabled()
    expect(screen.getByLabelText(/EAN/)).toBeInTheDocument()
    expect(screen.getByLabelText(/EAN/)).not.toBeDisabled()
    expect(screen.getByLabelText(/Intervenant/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Intervenant/)).not.toBeDisabled()
    expect(screen.getByLabelText(/Visa d’exploitation/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Visa d’exploitation/)).not.toBeDisabled()
    expect(screen.getByLabelText(/Metteur en scène/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Metteur en scène/)).not.toBeDisabled()
    expect(screen.getByLabelText(/Interprète/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Interprète/)).not.toBeDisabled()
    expect(screen.getByLabelText(/Durée/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Durée/)).not.toBeDisabled()
  })

  it('should disable read only fields', () => {
    props.readOnlyFields = [
      'name',
      'description',
      'author',
      'ean',
      'performer',
      'speaker',
      'stageDirector',
      'visa',
      'durationMinutes',
    ]

    initialValues.subCategoryFields = [
      'author',
      'ean',
      'performer',
      'speaker',
      'stageDirector',
      'visa',
      'durationMinutes',
    ]
    renderInformations({ props, initialValues, onSubmit })
    expect(screen.getByLabelText(/Titre de l’offre/)).toBeDisabled()
    expect(screen.getByLabelText(/Description/)).toBeDisabled()
    expect(screen.getByLabelText(/Auteur/)).toBeDisabled()
    expect(screen.getByLabelText(/EAN/)).toBeDisabled()
    expect(screen.getByLabelText(/Intervenant/)).toBeDisabled()
    expect(screen.getByLabelText(/Visa d’exploitation/)).toBeDisabled()
    expect(screen.getByLabelText(/Metteur en scène/)).toBeDisabled()
    expect(screen.getByLabelText(/Interprète/)).toBeDisabled()
    expect(screen.getByLabelText(/Durée/)).toBeDisabled()
  })
})
