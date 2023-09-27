import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { Audience } from 'core/shared'

import FilterByOmniSearch from '../FilterByOmniSearch'
import { FilterByOmniSearchProps } from '../FilterByOmniSearch/FilterByOmniSearch'

describe('components | FilterByOmniSearch', () => {
  let props: FilterByOmniSearchProps
  beforeEach(() => {
    props = {
      audience: Audience.INDIVIDUAL,
      keywords: '',
      selectedOmniSearchCriteria: 'offre',
      updateFilters: vi.fn(),
      isDisabled: false,
    }
  })

  it('should display a select input with the individual options', () => {
    // When
    render(<FilterByOmniSearch {...props} />)

    const options = screen.getAllByRole('option')

    // Then
    expect(screen.getByRole('combobox')).toBeInTheDocument()
    expect(options).toHaveLength(4)
    expect(options[0]).toHaveTextContent('Offre')
    expect(options[0]).toHaveValue('offre')
    expect(options[1]).toHaveTextContent('Bénéficiaire')
    expect(options[1]).toHaveValue('bénéficiaire')
    expect(options[2]).toHaveTextContent('EAN')
    expect(options[2]).toHaveValue('ean')
    expect(options[3]).toHaveTextContent('Contremarque')
    expect(options[3]).toHaveValue('contremarque')
  })

  it('should display a select input with the collective options', () => {
    // When
    render(<FilterByOmniSearch {...props} audience={Audience.COLLECTIVE} />)

    const options = screen.getAllByRole('option')

    // Then
    expect(screen.getByRole('combobox')).toBeInTheDocument()
    expect(options).toHaveLength(3)
    expect(options[0]).toHaveTextContent('Offre')
    expect(options[0]).toHaveValue('offre')
    expect(options[1]).toHaveTextContent('Établissement')
    expect(options[1]).toHaveValue('établissement')
    expect(options[2]).toHaveTextContent('Numéro de réservation')
    expect(options[2]).toHaveValue('booking_id')
  })

  it('should display the correct placeholder for current option selected', () => {
    // When
    render(<FilterByOmniSearch {...props} />)

    // Then
    expect(
      screen.getByPlaceholderText('Rechercher par nom d’offre')
    ).toBeInTheDocument()
  })

  it('should apply bookingBeneficiary filter when typing keywords for beneficiary name or email', async () => {
    // Given
    props.selectedOmniSearchCriteria = 'bénéficiaire'
    render(<FilterByOmniSearch {...props} />)
    screen.getByPlaceholderText('Rechercher par nom ou email').focus()

    // When
    await userEvent.paste('Firost')

    // Then
    expect(props.updateFilters).toHaveBeenCalledWith(
      {
        bookingBeneficiary: 'Firost',
        bookingToken: '',
        offerISBN: '',
        offerName: '',
        bookingInstitution: '',
        bookingId: '',
      },
      { keywords: 'Firost', selectedOmniSearchCriteria: 'bénéficiaire' }
    )
  })

  it('should update the selected omniSearch criteria when selecting an omniSearchCriteria', async () => {
    // Given
    props.keywords = '12548'
    render(<FilterByOmniSearch {...props} />)
    const omniSearchSelect = screen.getByRole('combobox')

    // When
    await userEvent.selectOptions(omniSearchSelect, 'ean')

    // Then
    expect(props.updateFilters).toHaveBeenCalledWith(
      {
        bookingBeneficiary: '',
        bookingToken: '',
        offerISBN: '12548',
        offerName: '',
        bookingInstitution: '',
        bookingId: '',
      },
      { keywords: '12548', selectedOmniSearchCriteria: 'ean' }
    )
  })
})
