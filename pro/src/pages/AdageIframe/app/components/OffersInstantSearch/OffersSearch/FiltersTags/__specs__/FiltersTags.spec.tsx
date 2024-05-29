import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import { OfferAddressType } from 'apiClient/adage'
import { renderWithProviders } from 'utils/renderWithProviders'

import { SearchFormValues } from '../../../OffersInstantSearch'
import { ADAGE_FILTERS_DEFAULT_VALUES } from '../../../utils'
import { LocalisationFilterStates } from '../../OffersSearch'
import { FiltersTags } from '../FiltersTags'

const domainsOptions = [
  { value: 1, label: 'Architecture' },
  { value: 2, label: 'Danse' },
]

const mockSetLocalisationFilterState = vi.fn()
const mockResetForm = vi.fn()
const renderFiltersTag = (
  initialValues: SearchFormValues,
  localisationFilterState?: LocalisationFilterStates
) => {
  renderWithProviders(
    <Formik initialValues={initialValues} onSubmit={vi.fn()}>
      <FiltersTags
        domainsOptions={domainsOptions}
        localisationFilterState={
          localisationFilterState || LocalisationFilterStates.NONE
        }
        setLocalisationFilterState={mockSetLocalisationFilterState}
        resetForm={mockResetForm}
      />
    </Formik>
  )
}
describe('FiltersTag', () => {
  const venueFilter = {
    id: 1,
    name: 'Mon super lieu',
    relative: [],
    departementCode: '75',
  }

  it('should display venue name in tag', () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      venue: venueFilter,
    })

    expect(screen.getByText(/Lieu : Mon super lieu/)).toBeInTheDocument()
  })
  it('should remove venue tag on click', async () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      venue: { ...venueFilter, publicName: 'Public name' },
    })
    await userEvent.click(
      screen.getByRole('button', { name: /Lieu : Public name/ })
    )
    expect(
      screen.queryByRole('button', { name: /Lieu : Public name/ })
    ).not.toBeInTheDocument()
  })

  it('should render in my school tag if event adress type school is selected', () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      eventAddressType: OfferAddressType.SCHOOL,
    })

    expect(
      screen.getByText(
        'Intervention d’un partenaire culturel dans mon établissement'
      )
    ).toBeInTheDocument()
  })
  it('should render in venue tag if event adress type school is selected', () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      eventAddressType: OfferAddressType.OFFERER_VENUE,
    })

    expect(
      screen.getByText('Sortie chez un partenaire culturel')
    ).toBeInTheDocument()
  })
  it('should remove tag on click', async () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      eventAddressType: OfferAddressType.OFFERER_VENUE,
    })
    await userEvent.click(
      screen.getByText('Sortie chez un partenaire culturel')
    )
    expect(
      screen.queryByText('Sortie chez un partenaire culturel')
    ).not.toBeInTheDocument()
  })

  it('should render geoLocation tag if geoLocation is selected', () => {
    renderFiltersTag(
      {
        ...ADAGE_FILTERS_DEFAULT_VALUES,
        geolocRadius: 10,
      },
      LocalisationFilterStates.GEOLOCATION
    )

    expect(
      screen.getByText('Localisation des partenaires : > à 10 km')
    ).toBeInTheDocument()
  })
  it('should remove geolocation tag on click', async () => {
    renderFiltersTag(
      {
        ...ADAGE_FILTERS_DEFAULT_VALUES,
        geolocRadius: 10,
      },
      LocalisationFilterStates.GEOLOCATION
    )
    await userEvent.click(
      screen.getByText('Localisation des partenaires : > à 10 km')
    )
    expect(
      screen.queryByText('Localisation des partenaires : > à 10 km')
    ).not.toBeInTheDocument()
    expect(mockSetLocalisationFilterState).toHaveBeenCalledWith(
      LocalisationFilterStates.NONE
    )
  })

  it('should display domain label in tag', () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      academies: ['Amiens', 'Paris'],
    })

    expect(screen.getByText('Amiens')).toBeInTheDocument()
    expect(screen.getByText('Paris')).toBeInTheDocument()
  })
  it('should remove domain tag on click', async () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      academies: ['Paris'],
    })
    await userEvent.click(screen.getByText('Paris'))
    expect(screen.queryByText('Paris')).not.toBeInTheDocument()
  })

  it('should display department label in tag', () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      departments: ['01', '75'],
    })

    expect(screen.getByText('01 - Ain')).toBeInTheDocument()
    expect(screen.getByText('75 - Paris')).toBeInTheDocument()
  })
  it('should not display tag if departement does not exit', () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      departments: ['abc123'],
    })

    expect(screen.queryByText('abc123')).not.toBeInTheDocument()
  })
  it('should remove department tag on click', async () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      departments: ['75'],
    })
    await userEvent.click(screen.getByText('75 - Paris'))
    expect(screen.queryByText('75 - Paris')).not.toBeInTheDocument()
    expect(mockSetLocalisationFilterState).toHaveBeenCalledWith(
      LocalisationFilterStates.NONE
    )
  })

  it('should display domain label in tag', () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      domains: [2],
    })

    expect(screen.getByText('Danse')).toBeInTheDocument()
  })
  it('should not display tag if domain does not exit', () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      domains: [12121212121],
    })

    expect(screen.queryByText('abc123')).not.toBeInTheDocument()
  })
  it('should remove domain tag on click', async () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      domains: [2],
    })
    await userEvent.click(screen.getByText('Danse'))
    expect(screen.queryByText('Danse')).not.toBeInTheDocument()
  })

  it('should display student label in tag', () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      students: ['Collège - 6e', 'Lycée - Seconde'],
    })

    expect(screen.getByText('Collège - 6e')).toBeInTheDocument()
    expect(screen.getByText('Lycée - Seconde')).toBeInTheDocument()
  })
  it('should remove student tag on click', async () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      students: ['Collège - 6e'],
    })
    await userEvent.click(screen.getByText('Collège - 6e'))
    expect(screen.queryByText('Collège - 6e')).not.toBeInTheDocument()
  })

  it('should call reinit filters on click reinit button', async () => {
    renderFiltersTag({
      ...ADAGE_FILTERS_DEFAULT_VALUES,
      departments: ['75'],
    })
    await userEvent.click(
      screen.getByRole('button', { name: 'Réinitialiser les filtres' })
    )
    expect(mockResetForm).toHaveBeenCalled()
  })
})
