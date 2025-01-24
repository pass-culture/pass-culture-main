import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'

import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { DEFAULT_EAC_FORM_VALUES } from 'commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { FormOfferType, FormTypeProps } from '../FormOfferType'

const mockLogEvent = vi.fn()

const renderFormOfferType = ({
  initialValues,
  props,
}: {
  initialValues: OfferEducationalFormValues
  props: FormTypeProps
}) => {
  return renderWithProviders(
    <Formik initialValues={initialValues} onSubmit={vi.fn()}>
      {({ handleSubmit }) => (
        <form onSubmit={handleSubmit}>
          <FormOfferType {...props} />
        </form>
      )}
    </Formik>
  )
}

describe('FormOfferType', () => {
  const formTypeProps: FormTypeProps = {
    disableForm: false,
    domainsOptions: [],
    nationalPrograms: [],
    isTemplate: false,
  }

  it('should offer the national program oprtions filtered for the selected domains', async () => {
    renderFormOfferType({
      initialValues: DEFAULT_EAC_FORM_VALUES,
      props: {
        ...formTypeProps,
        nationalPrograms: [
          { value: 4, label: 'Program 1' }, //  Program with id 4 should be displayed whatever the domain selection is
          { value: 11, label: 'Program 2' },
        ],
        domainsOptions: [],
      },
    })

    expect(
      await screen.findByRole('option', { name: 'Program 1' })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('option', { name: 'Program 2' })
    ).not.toBeInTheDocument()
  })

  it('should call tracker when clicking on template button', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    vi.spyOn(useAnalytics, 'useRemoteConfigParams').mockReturnValue({
      AB_COLLECTIVE_DESCRIPTION_TEMPLATE: 'true',
    })

    renderFormOfferType({
      initialValues: {
        ...DEFAULT_EAC_FORM_VALUES,
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
      name: 'Générer un exemple',
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
})
