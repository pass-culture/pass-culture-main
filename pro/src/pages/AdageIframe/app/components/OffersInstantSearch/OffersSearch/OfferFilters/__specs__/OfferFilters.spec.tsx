import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { AuthenticatedResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { AdageUserContext } from 'pages/AdageIframe/app/providers/AdageUserContext'
import * as pcapi from 'pages/AdageIframe/repository/pcapi/pcapi'
import { defaultAdageUser } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { LocalisationFilterStates, SearchFormValues } from '../../OffersSearch'
import { OfferFilters } from '../OfferFilters'

const handleSubmit = vi.fn()
const resetFormMock = vi.fn()
const mockSetLocalisationFilterState = vi.fn()

jest.mock('apiClient/api', () => ({
  apiAdage: {
    getAcademies: jest.fn(),
  },
}))
jest.mock('pages/AdageIframe/repository/pcapi/pcapi', () => ({
  getEducationalDomains: jest.fn(),
}))

const isGeolocationActive = {
  features: {
    list: [
      {
        nameKey: 'WIP_ENABLE_ADAGE_GEO_LOCATION',
        isActive: true,
      },
    ],
    initialized: true,
  },
}

const renderOfferFilters = ({
  initialValues,
  localisationFilterState = LocalisationFilterStates.NONE,
  adageUser = defaultAdageUser,
  storeOverrides = null,
}: {
  initialValues: SearchFormValues
  localisationFilterState?: LocalisationFilterStates
  adageUser?: AuthenticatedResponse
  storeOverrides?: unknown
}) =>
  renderWithProviders(
    <AdageUserContext.Provider value={{ adageUser: adageUser }}>
      <Formik initialValues={initialValues} onSubmit={handleSubmit}>
        <OfferFilters
          localisationFilterState={localisationFilterState}
          setLocalisationFilterState={mockSetLocalisationFilterState}
          resetForm={resetFormMock}
        />
      </Formik>
    </AdageUserContext.Provider>,
    { storeOverrides: storeOverrides }
  )

const initialValues = {
  query: '',
  domains: [],
  students: [],
  eventAddressType: '',
  departments: [],
  academies: [],
  categories: [],
  geolocRadius: 50,
}

describe('OfferFilters', () => {
  it('renders correctly', () => {
    renderOfferFilters({ initialValues })

    expect(
      screen.getByRole('button', { name: 'Domaine artistique' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Niveau scolaire' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Type d’intervention' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Catégorie' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    ).toBeInTheDocument()
  })

  it('should submit onclick modal search button domain artistic', async () => {
    renderOfferFilters({
      initialValues: {
        ...initialValues,
        domains: ['test'],
      },
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Domaine artistique (1)' })
    )

    await userEvent.click(screen.getAllByTestId('search-button-modal')[0])

    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should submit onclick modal search button cateogires', async () => {
    renderOfferFilters({
      initialValues: {
        ...initialValues,
        categories: [['test']],
      },
    })

    await userEvent.click(screen.getByRole('button', { name: 'Catégorie (1)' }))

    await userEvent.click(screen.getAllByTestId('search-button-modal')[0])

    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should submit onclick modal search button school level', async () => {
    renderOfferFilters({
      initialValues: {
        ...initialValues,
        students: ['test'],
      },
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Niveau scolaire (1)' })
    )

    await userEvent.click(screen.getAllByTestId('search-button-modal')[1])

    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should reset filter onclick modal clear artistic domain', async () => {
    renderOfferFilters({
      initialValues: {
        ...initialValues,
        domains: ['test'],
      },
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
      initialValues: {
        ...initialValues,
        students: ['test'],
      },
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
    vi.spyOn(pcapi, 'getEducationalDomains').mockResolvedValueOnce([
      { id: 1, name: 'Danse' },
      { id: 2, name: 'Architecture' },
      { id: 3, name: 'Arts' },
    ])

    renderOfferFilters({
      initialValues: initialValues,
    })

    await userEvent.click(
      screen.getByRole('button', { name: 'Domaine artistique' })
    )

    expect(screen.getByText('Danse')).toBeInTheDocument()
    expect(screen.getByText('Architecture')).toBeInTheDocument()
    expect(screen.getByText('Arts')).toBeInTheDocument()
  })

  it('should display departments and academies button in localisation filter modal', async () => {
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.NONE,
      adageUser: { ...defaultAdageUser },
    })

    expect(screen.getByText('Choisir un département')).toBeInTheDocument()
    expect(screen.getByText('Choisir une académie')).toBeInTheDocument()
  })

  it('should display geoloc button in localisation filter modal', async () => {
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.NONE,
      adageUser: { ...defaultAdageUser, lat: 10, lon: 10 },
      storeOverrides: isGeolocationActive,
    })

    expect(
      screen.getByText('Autour de mon établissement scolaire')
    ).toBeInTheDocument()
  })

  it('should not display geoloc button in localisation filter modal if the user does not have a valid geoloc', async () => {
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.NONE,
      adageUser: { ...defaultAdageUser, lat: 10, lon: null },
      storeOverrides: isGeolocationActive,
    })

    expect(
      screen.queryByText('Autour de mon établissement scolaire')
    ).not.toBeInTheDocument()
  })

  it('should display departments options in localisation filter modal', async () => {
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.DEPARTMENTS,
    })

    expect(
      screen.getByPlaceholderText('Ex: 59 ou Hauts-de-France')
    ).toBeInTheDocument()
  })
  it('should display academies options in localisation filter modal', async () => {
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.ACADEMIES,
    })

    expect(screen.getByPlaceholderText('Ex: Nantes')).toBeInTheDocument()
  })

  it('should display radius range input in localisation filter modal', async () => {
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.GEOLOCATION,
      storeOverrides: isGeolocationActive,
    })

    expect(screen.getByText('Dans un rayon de')).toBeInTheDocument()
    expect(screen.getByText('50 km')).toBeInTheDocument()
  })

  it('should reset modal state when closing departments filter modal', async () => {
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.DEPARTMENTS,
    })

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
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.ACADEMIES,
    })

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
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.GEOLOCATION,
      storeOverrides: isGeolocationActive,
    })

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
    renderOfferFilters({
      initialValues: initialValues,
      localisationFilterState: LocalisationFilterStates.GEOLOCATION,
      storeOverrides: isGeolocationActive,
    })

    await userEvent.click(
      screen.getByRole('button', {
        name: /Localisation des partenaires/,
      })
    )
    screen.debug()
    await userEvent.click(screen.getAllByTestId('search-button-modal')[0])

    expect(handleSubmit).toHaveBeenCalled()
  })

  it('should return categories options when the api call was successful', async () => {
    vi.spyOn(apiAdage, 'getEducationalOffersCategories').mockResolvedValueOnce({
      categories: [{ id: 'CINEMA', proLabel: 'Cinéma' }],
      subcategories: [{ id: 'CINE_PLEIN_AIR', categoryId: 'CINEMA' }],
    })

    renderOfferFilters({
      initialValues: initialValues,
      storeOverrides: isGeolocationActive,
    })

    await userEvent.click(screen.getByRole('button', { name: 'Catégorie' }))

    expect(screen.getByText('Cinéma')).toBeInTheDocument()
  })
})
