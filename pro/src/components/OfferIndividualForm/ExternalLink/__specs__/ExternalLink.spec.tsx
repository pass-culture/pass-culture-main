import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { OfferIndividualFormValues } from 'components/OfferIndividualForm'
import { SubmitButton } from 'ui-kit'

import { EXTERNAL_LINK_DEFAULT_VALUES } from '../constants'
import ExternalLink, { ExternalLinkProps } from '../ExternalLink'
import validationSchema from '../validationSchema'

const renderExternalLink = ({
  props,
  initialValues,
  onSubmit,
}: {
  props?: ExternalLinkProps
  initialValues: Partial<OfferIndividualFormValues>
  onSubmit: () => void
}) => {
  render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Form>
        <ExternalLink {...props} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('OfferIndividual section: ExternalLink', () => {
  let initialValues: Partial<OfferIndividualFormValues>
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = { ...EXTERNAL_LINK_DEFAULT_VALUES }
  })

  it('should render the component', () => {
    renderExternalLink({
      initialValues,
      onSubmit,
    })
    expect(screen.getByText('Lien pour le grand public')).toBeInTheDocument()
    expect(
      screen.getByLabelText('URL de votre site ou billetterie', {
        exact: false,
      })
    ).toBeInTheDocument()

    const infoBox = screen.getByText(
      'Ce lien sera affiché au public souhaitant réserver l’offre mais ne disposant pas ou plus de crédit sur l’application.'
    )
    expect(infoBox).toBeInTheDocument()
  })

  it('should submit valid form', async () => {
    renderExternalLink({
      initialValues,
      onSubmit,
    })
    const urlInput = screen.getByLabelText('URL de votre site ou billetterie', {
      exact: false,
    })

    await userEvent.type(urlInput, 'https://example.com')
    await userEvent.click(screen.getByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      { externalTicketOfficeUrl: 'https://example.com' },
      expect.anything()
    )
  })

  it('should submit empty valid form', async () => {
    renderExternalLink({
      initialValues,
      onSubmit,
    })

    await userEvent.click(screen.getByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      { externalTicketOfficeUrl: '' },
      expect.anything()
    )
  })

  it('should display errors when url is wrong', async () => {
    renderExternalLink({
      initialValues,
      onSubmit,
    })
    const urlInput = screen.getByLabelText('URL de votre site ou billetterie', {
      exact: false,
    })

    await userEvent.type(urlInput, 'fake url')
    await userEvent.tab()

    const errorMessage = screen.getByText(
      'Veuillez renseigner une URL valide. Ex : https://exemple.com'
    )
    expect(errorMessage).toBeInTheDocument()

    await userEvent.clear(urlInput)
    await userEvent.type(urlInput, 'https://example.com')

    expect(
      screen.queryByText(
        'Veuillez renseigner une URL valide. Ex : https://exemple.com'
      )
    ).not.toBeInTheDocument()
  })

  it('should disable read only fields', () => {
    const props = { readOnlyFields: ['externalTicketOfficeUrl'] }
    renderExternalLink({
      props,
      initialValues,
      onSubmit,
    })
    expect(
      screen.getByLabelText('URL de votre site ou billetterie', {
        exact: false,
      })
    ).toBeDisabled()
  })
})
