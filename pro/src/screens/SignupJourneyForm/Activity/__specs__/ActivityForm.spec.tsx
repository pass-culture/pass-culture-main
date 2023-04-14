import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import { api } from 'apiClient/api'
import { Target, VenueTypeCode } from 'apiClient/v1'
import {
  ISignupJourneyContext,
  SignupJourneyContext,
} from 'context/SignupJourneyContext'
import { SubmitButton } from 'ui-kit'
import { renderWithProviders } from 'utils/renderWithProviders'

import ActivityForm, {
  IActivityFormProps,
  IActivityFormValues,
} from '../ActivityForm'
import { DEFAULT_ACTIVITY_FORM_VALUES } from '../constants'
import { validationSchema } from '../validationSchema'

jest.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: jest.fn(),
  },
}))

const venueTypes: SelectOption[] = [
  { value: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { value: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const renderActivityForm = ({
  initialValues,
  onSubmit = jest.fn(),
  props = { venueTypes: venueTypes },
  contextValue,
}: {
  initialValues: Partial<IActivityFormValues>
  onSubmit?: () => void
  props: IActivityFormProps
  contextValue: ISignupJourneyContext
}) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
  }

  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={validationSchema}
      >
        <Form>
          <ActivityForm {...props} />
          <SubmitButton isLoading={false}>Submit</SubmitButton>
        </Form>
      </Formik>
    </SignupJourneyContext.Provider>,
    { storeOverrides, initialRouterEntries: ['/parcours-inscription/activite'] }
  )
}

describe('screens:SignupJourney::ActivityForm', () => {
  let activity: IActivityFormValues
  let contextValue: ISignupJourneyContext
  let props: IActivityFormProps
  let initialValues: Partial<IActivityFormValues>
  beforeEach(() => {
    activity = DEFAULT_ACTIVITY_FORM_VALUES
    initialValues = { ...activity }
    props = {
      venueTypes: venueTypes,
    }
    contextValue = {
      activity: activity,
      offerer: null,
      setActivity: () => {},
      setOfferer: () => {},
    }
    jest.spyOn(api, 'getVenueTypes').mockResolvedValue([])
  })

  it('should render activity form', async () => {
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })
    expect(await screen.findByText('Activité')).toBeInTheDocument()
    expect(await screen.getByLabelText('Activité principale')).toHaveValue('')
    expect(
      await screen.getAllByText('Site internet, réseau social')
    ).toHaveLength(1)
    expect(
      await screen.findByRole('button', { name: 'Ajouter un lien' })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('À destination du grand public', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText("À destination d'un groupe scolaire", {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText('Les deux', {
        exact: false,
      })
    ).not.toBeChecked()
  })

  it('should render activity form with initialValues', async () => {
    initialValues = {
      venueTypeCode: VenueTypeCode.MUS_E,
      socialUrls: ['https://example.com', 'https://exampleTwo.fr'],
      targetCustomer: Target.INDIVIDUAL_AND_EDUCATIONAL,
    }
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })
    expect(
      await screen.getByText('Cours et pratique artistiques')
    ).toBeInTheDocument()
    expect(
      await screen.getAllByText('Site internet, réseau social')
    ).toHaveLength(2)
    expect(
      screen.getByLabelText('À destination du grand public', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText("À destination d'un groupe scolaire", {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText('Les deux', {
        exact: false,
      })
    ).toBeChecked()
  })

  it('should render errors', async () => {
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })

    expect(await screen.findByText('Activité')).toBeInTheDocument()
    await userEvent.type(
      screen.getByPlaceholderText('https://www.siteinternet.com'),
      'qsdsqd'
    )
    await userEvent.click(screen.getByText('Submit'))
    expect(
      await screen.findByText(
        'Veuillez sélectionner une des réponses ci-dessus'
      )
    ).toBeInTheDocument()
    expect(
      await screen.findByText('Veuillez sélectionner une activité principale')
    ).toBeInTheDocument()
    expect(
      await screen.findByText(
        'Veuillez renseigner une URL valide. Ex : https://exemple.com'
      )
    ).toBeInTheDocument()
  })

  it('should add social url input on click add url button', async () => {
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })

    expect(await screen.findByText('Activité')).toBeInTheDocument()
    expect(
      await screen.getAllByText('Site internet, réseau social')
    ).toHaveLength(1)
    await userEvent.click(screen.getByText('Ajouter un lien'))
    expect(
      await screen.getAllByText('Site internet, réseau social')
    ).toHaveLength(2)
  })

  it('should remove social url input on click remove url button', async () => {
    initialValues.socialUrls = ['https://example.com', 'https://exampleTwo.fr']
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })

    expect(
      await screen.getAllByText('Site internet, réseau social')
    ).toHaveLength(2)

    const trashButtons = await screen.getAllByRole('button', {
      name: "Supprimer l'url",
    })

    await userEvent.click(trashButtons[0])
    expect(
      await screen.getAllByText('Site internet, réseau social')
    ).toHaveLength(1)
    expect(screen.queryByText('https://example.fr')).not.toBeInTheDocument()
    expect(
      screen.getByDisplayValue('https://exampleTwo.fr')
    ).toBeInTheDocument()
  })

  it('should change targetCustomer value on click', async () => {
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })

    const publicTarget = screen.getByLabelText('À destination du grand public')
    const schoolTarget = screen.getByLabelText(
      "À destination d'un groupe scolaire"
    )
    const allTarget = screen.getByLabelText('Les deux')

    expect(publicTarget).not.toBeChecked()
    expect(allTarget).not.toBeChecked()
    expect(schoolTarget).not.toBeChecked()

    await userEvent.click(publicTarget)
    expect(publicTarget).toBeChecked()

    await userEvent.click(schoolTarget)
    expect(schoolTarget).toBeChecked()
    expect(publicTarget).not.toBeChecked()

    await userEvent.click(allTarget)
    expect(allTarget).toBeChecked()
    expect(publicTarget).not.toBeChecked()
    expect(schoolTarget).not.toBeChecked()
  })

  it('should change venueType', async () => {
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })

    const venueTypeSelect = await screen.getByLabelText('Activité principale')
    expect(venueTypeSelect).toHaveValue('')

    await userEvent.click(await venueTypeSelect)
    await userEvent.click(await screen.getByText('Culture scientifique'))
    await waitFor(() => {
      expect(screen.getByText('Culture scientifique')).toBeInTheDocument()
    })
  })
})
