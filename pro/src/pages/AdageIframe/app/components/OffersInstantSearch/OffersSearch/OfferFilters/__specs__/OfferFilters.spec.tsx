import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import {
  CollectiveLocationType,
  EacFormat,
  OfferAddressType,
} from 'apiClient/adage'
import { defaultAdageUser } from 'commons/utils/factories/adageFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'

import { SearchFormValues } from '../../../OffersInstantSearch'
import { LocalisationFilterStates } from '../../OffersSearch'
import { OfferFilters } from '../OfferFilters'

const handleSubmit = vi.fn()
const mockSetLocalisationFilterState = vi.fn()

vi.mock('apiClient/api', () => ({
  apiAdage: {
    getAcademies: vi.fn(),
  },
}))

const renderOfferFilters = (
  initialValues: SearchFormValues,
  localisationFilterState = LocalisationFilterStates.NONE,
  adageUser = defaultAdageUser,
  options?: RenderWithProvidersOptions
) =>
  renderWithProviders(
    <AdageUserContextProvider adageUser={adageUser}>
      <Formik initialValues={initialValues} onSubmit={handleSubmit}>
        <OfferFilters
          localisationFilterState={localisationFilterState}
          setLocalisationFilterState={mockSetLocalisationFilterState}
          domainsOptions={[
            { value: 1, label: 'Danse' },
            { value: 2, label: 'Architecture' },
            { value: 3, label: 'Arts' },
          ]}
          shouldDisplayMarseilleStudentOptions={true}
        />
      </Formik>
    </AdageUserContextProvider>,
    options
  )

const initialValues = {
  query: '',
  domains: [],
  students: [],
  eventAddressType: '',
  locationType: '',
  departments: [],
  academies: [],
  formats: [],
  geolocRadius: 50,
  venue: null,
}

describe('OfferFilters', () => {
  it('should submit onclick modal search button domain artistic', async () => {
    renderOfferFilters({
      ...initialValues,
      domains: [123],
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Domaine artistique (1)' })
    )

    await userEvent.click(screen.getAllByTestId('search-button-modal')[0])

    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should submit formats values onclick modal search button', async () => {
    renderOfferFilters({
      ...initialValues,
      formats: [EacFormat.CONCERT, EacFormat.REPR_SENTATION],
    })

    await userEvent.click(screen.getByRole('button', { name: 'Format (2)' }))

    await userEvent.click(screen.getAllByTestId('search-button-modal')[0])

    expect(handleSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        ...initialValues,
        formats: [EacFormat.CONCERT, EacFormat.REPR_SENTATION],
      }),
      expect.anything()
    )
  })

  it('should submit onclick modal search button school level', async () => {
    renderOfferFilters({
      ...initialValues,
      students: ['test'],
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Niveau scolaire (1)' })
    )

    await userEvent.click(screen.getAllByTestId('search-button-modal')[1])

    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should reset filter onclick modal clear artistic domain', async () => {
    renderOfferFilters({
      ...initialValues,
      domains: [123],
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Domaine artistique (1)' })
    )

    await userEvent.click(screen.getByRole('button', { name: 'Réinitialiser' }))

    expect(
      screen.getByRole('button', { name: 'Domaine artistique' })
    ).toBeInTheDocument()
  })

  it('should reset filter onclick modal clear students', async () => {
    renderOfferFilters({
      ...initialValues,
      students: ['test'],
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Niveau scolaire (1)' })
    )

    await userEvent.click(screen.getByRole('button', { name: 'Réinitialiser' }))

    expect(
      screen.getByRole('button', { name: 'Niveau scolaire' })
    ).toBeInTheDocument()
  })

  it('should return domains options when the api call was successful', async () => {
    renderOfferFilters(initialValues)

    await userEvent.click(
      screen.getByRole('button', { name: 'Domaine artistique' })
    )

    expect(screen.getByText('Danse')).toBeInTheDocument()
    expect(screen.getByText('Architecture')).toBeInTheDocument()
    expect(screen.getByText('Arts')).toBeInTheDocument()
  })

  it('should display departments and academies button in localisation filter modal', () => {
    renderOfferFilters(
      initialValues,
      LocalisationFilterStates.NONE,
      defaultAdageUser
    )

    expect(screen.getByText('Choisir un département')).toBeInTheDocument()
    expect(screen.getByText('Choisir une académie')).toBeInTheDocument()
  })

  it('should display geoloc button in localisation filter modal', () => {
    renderOfferFilters(initialValues, LocalisationFilterStates.NONE, {
      ...defaultAdageUser,
      lat: 10,
      lon: 10,
    })

    expect(
      screen.getByText('Autour de mon établissement scolaire')
    ).toBeInTheDocument()
  })

  it('should not display geoloc button in localisation filter modal if the user does not have a valid geoloc', () => {
    renderOfferFilters(initialValues, LocalisationFilterStates.NONE, {
      ...defaultAdageUser,
      lat: 10,
      lon: null,
    })

    expect(
      screen.queryByText('Autour de mon établissement scolaire')
    ).not.toBeInTheDocument()
  })

  it('should display departments options in localisation filter modal', async () => {
    renderOfferFilters(initialValues, LocalisationFilterStates.DEPARTMENTS)

    await userEvent.click(
      screen.getByRole('button', { name: 'Localisation des partenaires' })
    )

    expect(
      screen.getByRole('checkbox', { name: '01 - Ain' })
    ).toBeInTheDocument()
  })
  it('should display academies options in localisation filter modal', async () => {
    renderOfferFilters(initialValues, LocalisationFilterStates.ACADEMIES)

    await userEvent.click(
      screen.getByRole('button', { name: 'Localisation des partenaires' })
    )

    expect(
      screen.getByRole('listbox', { name: 'Rechercher une académie' })
    ).toBeInTheDocument()
  })

  it('should display radius range input in localisation filter modal', () => {
    renderOfferFilters(initialValues, LocalisationFilterStates.GEOLOCATION)

    expect(screen.getByText('Dans un rayon de')).toBeInTheDocument()
    expect(screen.getByText('50 km')).toBeInTheDocument()
  })

  it('should reset modal state when closing departments filter modal', async () => {
    renderOfferFilters(initialValues, LocalisationFilterStates.DEPARTMENTS)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires',
      })
    )
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Réinitialiser',
      })
    )

    expect(mockSetLocalisationFilterState).toHaveBeenCalledWith(
      LocalisationFilterStates.NONE
    )
  })
  it('should reset modal state when closing academies filter modal', async () => {
    renderOfferFilters(initialValues, LocalisationFilterStates.ACADEMIES)

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Localisation des partenaires',
      })
    )
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Réinitialiser',
      })
    )

    expect(mockSetLocalisationFilterState).toHaveBeenCalledWith(
      LocalisationFilterStates.NONE
    )
  })

  it('should reset modal state when closing geoloc filter modal', async () => {
    renderOfferFilters(initialValues, LocalisationFilterStates.GEOLOCATION)

    await userEvent.click(
      screen.getByRole('button', {
        name: /Localisation des partenaires/,
      })
    )
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Réinitialiser',
      })
    )

    expect(mockSetLocalisationFilterState).toHaveBeenCalledWith(
      LocalisationFilterStates.NONE
    )
  })

  it('should trigger search when clicking Rechercher while using geoloc', async () => {
    renderOfferFilters(initialValues, LocalisationFilterStates.GEOLOCATION)

    await userEvent.click(
      screen.getByRole('button', {
        name: /Localisation des partenaires/,
      })
    )
    await userEvent.click(screen.getAllByTestId('search-button-modal')[0])

    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should sort students options with selected first but keep initial order otherwise', async () => {
    renderOfferFilters({
      ...initialValues,
      students: ['Collège - 5e'],
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Niveau scolaire (1)' })
    )

    const options = screen.getAllByRole('checkbox')

    //  Verify that the selected option comes first
    expect(options[0]).toHaveAccessibleName('Collège - 5e')

    //  Verify that non-selected options aren't sorted alphabetically
    expect(options[1]).toHaveAccessibleName('Écoles Marseille - Maternelle')
    expect(options[options.length - 1]).toHaveAccessibleName('CAP - 2e année')
  })

  it('should display all intervention type options', async () => {
    renderOfferFilters(initialValues)

    await userEvent.click(
      screen.getByRole('button', { name: 'Type d’intervention' })
    )

    expect(
      screen.getByRole('radio', {
        name: 'Je n’ai pas de préférence (Voir tout)',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', { name: 'Sortie chez un partenaire culturel' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radio', {
        name: 'Intervention d’un partenaire culturel dans mon établissement',
      })
    ).toBeInTheDocument()
  })

  it('should verify radio filter value "Sortie chez un partenaire culturel"', async () => {
    renderOfferFilters(initialValues)

    await userEvent.click(
      screen.getByRole('button', { name: 'Type d’intervention' })
    )

    const radioButton = screen.getByRole('radio', {
      name: 'Sortie chez un partenaire culturel',
    })

    expect(radioButton).toHaveAttribute('value', OfferAddressType.OFFERER_VENUE)
  })

  it('should verify radio filter value is OFFERER_VENUE for "Sortie chez un partenaire culturel"', async () => {
    renderOfferFilters(initialValues)

    await userEvent.click(
      screen.getByRole('button', { name: 'Type d’intervention' })
    )

    const radioButton = screen.getByRole('radio', {
      name: 'Sortie chez un partenaire culturel',
    })

    expect(radioButton).toHaveAttribute('value', OfferAddressType.OFFERER_VENUE)
  })

  it('should verify radio filter value is ADDRESS for "Sortie chez un partenaire culturel" when FF OA is enabled', async () => {
    renderOfferFilters(
      initialValues,
      LocalisationFilterStates.NONE,
      defaultAdageUser,
      {
        features: ['WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'],
      }
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Type d’intervention' })
    )

    const radioButton = screen.getByRole('radio', {
      name: 'Sortie chez un partenaire culturel',
    })

    expect(radioButton).toHaveAttribute('value', CollectiveLocationType.ADDRESS)
  })

  it('should verify radio filter value is SCHOOL for "Intervention d’un partenaire culturel dans mon établissement"', async () => {
    renderOfferFilters(initialValues)

    await userEvent.click(
      screen.getByRole('button', { name: 'Type d’intervention' })
    )

    const radioButton = screen.getByRole('radio', {
      name: 'Intervention d’un partenaire culturel dans mon établissement',
    })

    expect(radioButton).toHaveAttribute('value', OfferAddressType.SCHOOL)
  })

  it('should verify radio filter value is SCHOOL for "Intervention d’un partenaire culturel dans mon établissement" when FF OA is enabled', async () => {
    renderOfferFilters(
      initialValues,
      LocalisationFilterStates.NONE,
      defaultAdageUser,
      {
        features: ['WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'],
      }
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Type d’intervention' })
    )

    const radioButton = screen.getByRole('radio', {
      name: 'Intervention d’un partenaire culturel dans mon établissement',
    })

    expect(radioButton).toHaveAttribute('value', CollectiveLocationType.SCHOOL)
  })
})
