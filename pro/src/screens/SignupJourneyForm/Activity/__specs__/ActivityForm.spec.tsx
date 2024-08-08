import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import { api } from 'apiClient/api'
import { VenueTypeResponseModel } from 'apiClient/v1'
import { DEFAULT_ACTIVITY_VALUES } from 'context/SignupJourneyContext/constants'
import {
  ActivityContext,
  SignupJourneyContext,
  SignupJourneyContextValues,
} from 'context/SignupJourneyContext/SignupJourneyContext'
import { Button } from 'ui-kit/Button/Button'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  ActivityForm,
  ActivityFormProps,
  ActivityFormValues,
} from '../ActivityForm'
import { DEFAULT_ACTIVITY_FORM_VALUES } from '../constants'
import { validationSchema } from '../validationSchema'

vi.mock('apiClient/api', () => ({
  api: {
    getVenueTypes: vi.fn(),
  },
}))

const venueTypes: VenueTypeResponseModel[] = [
  { id: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { id: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const renderActivityForm = ({
  initialValues,
  onSubmit = vi.fn(),
  props = { venueTypes: venueTypes },
  contextValue,
}: {
  initialValues: Partial<ActivityFormValues>
  onSubmit?: () => void
  props: ActivityFormProps
  contextValue: SignupJourneyContextValues
}) => {
  return renderWithProviders(
    <SignupJourneyContext.Provider value={contextValue}>
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={validationSchema}
      >
        <Form noValidate>
          <ActivityForm {...props} />
          <Button type="submit" isLoading={false}>
            Submit
          </Button>
        </Form>
      </Formik>
    </SignupJourneyContext.Provider>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/parcours-inscription/activite'],
    }
  )
}

describe('screens:SignupJourney::ActivityForm', () => {
  let activity: ActivityContext
  let contextValue: SignupJourneyContextValues
  let props: ActivityFormProps
  let initialValues: Partial<ActivityFormValues>
  beforeEach(() => {
    activity = DEFAULT_ACTIVITY_VALUES
    initialValues = DEFAULT_ACTIVITY_FORM_VALUES
    props = {
      venueTypes: venueTypes,
    }
    contextValue = {
      activity: activity,
      offerer: null,
      setActivity: () => {},
      setOfferer: () => {},
    }
    vi.spyOn(api, 'getVenueTypes').mockResolvedValue([])
  })

  it('should render activity form', async () => {
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })
    expect(await screen.findByText('Activité')).toBeInTheDocument()
    expect(screen.getByLabelText('Activité principale *')).toHaveValue('')
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(1)
    expect(
      await screen.findByRole('button', { name: 'Ajouter un lien' })
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText('Au grand public', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText('À des groupes scolaires', {
        exact: false,
      })
    ).not.toBeChecked()
  })

  it('should render activity form with initialValues', () => {
    initialValues = {
      venueTypeCode: 'MUSEUM',
      socialUrls: ['https://example.com', 'https://exampleTwo.fr'],
      targetCustomer: { individual: false, educational: false },
    }
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })
    expect(
      screen.getByText('Cours et pratique artistiques')
    ).toBeInTheDocument()
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(2)
    expect(
      screen.getByLabelText('Au grand public', {
        exact: false,
      })
    ).not.toBeChecked()
    expect(
      screen.getByLabelText('À des groupes scolaires', {
        exact: false,
      })
    ).not.toBeChecked()
  })

  it('should render errors', async () => {
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })

    expect(await screen.findByText('Activité')).toBeInTheDocument()
    await userEvent.type(
      screen.getByRole('textbox', {
        name: 'Site internet, réseau social',
      }),
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
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(1)
    await userEvent.click(screen.getByText('Ajouter un lien'))
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(2)
  })

  it('should remove social url input on click remove url button', async () => {
    initialValues.socialUrls = ['https://example.com', 'https://exampleTwo.fr']
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })

    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(2)

    const trashButtons = screen.getAllByRole('button', {
      name: 'Supprimer l’url',
    })

    await userEvent.click(trashButtons[0])
    expect(screen.getAllByText('Site internet, réseau social')).toHaveLength(1)
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

    const publicTarget = screen.getByLabelText('Au grand public')
    const schoolTarget = screen.getByLabelText('À des groupes scolaires')

    expect(publicTarget).not.toBeChecked()
    expect(schoolTarget).not.toBeChecked()

    await userEvent.click(publicTarget)
    expect(publicTarget).toBeChecked()

    await userEvent.click(schoolTarget)
    expect(schoolTarget).toBeChecked()
    expect(publicTarget).toBeChecked()

    await userEvent.click(publicTarget)
    expect(schoolTarget).toBeChecked()
    expect(publicTarget).not.toBeChecked()
  })

  it('should change venueType', async () => {
    renderActivityForm({
      initialValues: initialValues,
      props: props,
      contextValue,
    })

    const venueTypeSelect = screen.getByLabelText('Activité principale *')
    expect(venueTypeSelect).toHaveValue('')

    await userEvent.click(venueTypeSelect)
    await userEvent.click(screen.getByText('Culture scientifique'))
    await waitFor(() => {
      expect(screen.getByText('Culture scientifique')).toBeInTheDocument()
    })
  })
})
