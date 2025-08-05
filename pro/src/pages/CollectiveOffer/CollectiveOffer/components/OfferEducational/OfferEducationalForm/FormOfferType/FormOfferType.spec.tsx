import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { getDefaultEducationalValues } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { FormProvider, useForm } from 'react-hook-form'

import { FormOfferType, FormTypeProps } from './FormOfferType'

const mockLogEvent = vi.fn()

function renderFormOfferType({
  initialValues,
  props,
}: {
  initialValues: OfferEducationalFormValues
  props: FormTypeProps
}) {
  function FormOfferTypeWrapper() {
    const form = useForm({
      defaultValues: initialValues,
    })

    return (
      <FormProvider {...form}>
        <FormOfferType {...props} />
      </FormProvider>
    )
  }

  return renderWithProviders(<FormOfferTypeWrapper />)
}

describe('FormOfferType', () => {
  const formTypeProps: FormTypeProps = {
    disableForm: false,
    domainsOptions: [],
    isTemplate: false,
  }

  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should offer the national program options filtered for the selected domains', async () => {
    renderFormOfferType({
      initialValues: getDefaultEducationalValues(),
      props: {
        ...formTypeProps,
        domainsOptions: [
          {
            label: 'Domain 1',
            id: '1',
            nationalPrograms: [{ id: 1, name: 'nationalProgram1' }],
          },
          {
            label: 'Domain 2',
            id: '2',
            nationalPrograms: [{ id: 2, name: 'nationalProgram2' }],
          },
        ],
      },
    })

    const domainsSelect = await screen.findByLabelText(/Domaines artistiques */)
    await userEvent.click(domainsSelect)
    await userEvent.click(await screen.findByText('Domain 1'))

    expect(
      await screen.findByRole('option', { name: 'nationalProgram1' })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('option', { name: 'nationalProgram2' })
    ).not.toBeInTheDocument()
  })

  it('should select the existing national program', async () => {
    renderFormOfferType({
      initialValues: {
        ...getDefaultEducationalValues(),
        domains: ['1'],
        nationalProgramId: '1',
      },
      props: {
        ...formTypeProps,
        domainsOptions: [
          {
            label: 'Domain 1',
            id: '1',
            nationalPrograms: [{ id: 1, name: 'nationalProgram1' }],
          },
          {
            label: 'Domain 2',
            id: '2',
            nationalPrograms: [{ id: 2, name: 'nationalProgram2' }],
          },
        ],
      },
    })

    expect(
      await screen.findByRole('option', { name: 'nationalProgram1' })
    ).toBeInTheDocument()
  })

  it('should call tracker when clicking on template button', async () => {
    renderFormOfferType({
      initialValues: {
        ...getDefaultEducationalValues(),
        offererId: '1',
        venueId: '2',
        domains: ['1', '2'],
      },
      props: {
        ...formTypeProps,
        isTemplate: true,
      },
    })

    const templateButton = screen.getByRole('button', {
      name: 'Générer un modèle',
    })

    await userEvent.click(templateButton)

    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_GENERATE_TEMPLATE_DESCRIPTION,
      {
        offererId: '1',
        venueId: '2',
        domainIds: [1, 2],
      }
    )
  })

  it('should not see template examples faq on bookable offer form', () => {
    renderFormOfferType({
      initialValues: getDefaultEducationalValues(),
      props: {
        ...formTypeProps,
        isTemplate: false,
      },
    })

    const seeExamplesButton = screen.queryByText(
      'Voir des exemples d’offres vitrines'
    )

    expect(seeExamplesButton).not.toBeInTheDocument()
  })

  it('should call tracker when clicking on "Voir des exemples" button', async () => {
    renderFormOfferType({
      initialValues: {
        ...getDefaultEducationalValues(),
        offererId: '1',
        venueId: '2',
        domains: ['1', '2'],
      },
      props: {
        ...formTypeProps,
        isTemplate: true,
      },
    })

    const seeExamplesButton = screen.getByText(
      'Voir des exemples d’offres vitrines'
    )

    await userEvent.click(seeExamplesButton)

    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE,
      {
        offererId: '1',
        venueId: '2',
        domainIds: [1, 2],
      }
    )
  })
})
