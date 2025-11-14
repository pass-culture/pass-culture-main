import { screen } from '@testing-library/react'
import { describe } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferInstitutionCell,
  type OfferInstitutionCellProps,
} from './OfferInstitutionCell'

const props = {
  educationalInstitution: {
    id: 1,
    name: 'Collège Bellevue',
    city: 'Rouen',
    postalCode: '76000',
    phoneNumber: '0102030405',
    institutionId: 'XYZ123',
    institutionType: 'COLLEGE',
  },
}

const renderOfferInstitutionCell = (props: OfferInstitutionCellProps) =>
  renderWithProviders(<OfferInstitutionCell {...props} />)

describe('OfferInstitutionCell', () => {
  it('should display the full institution name and postal code when provided', () => {
    renderOfferInstitutionCell({
      ...props,
      educationalInstitution: {
        ...props.educationalInstitution,
        postalCode: '76000',
      },
    })

    expect(screen.getByText('Collège Bellevue')).toBeInTheDocument()
    expect(screen.getByText('76000')).toBeInTheDocument()
  })

  it('should display institutionType, city and postalCode when name is not provided', () => {
    renderOfferInstitutionCell({
      ...props,
      educationalInstitution: {
        ...props.educationalInstitution,
        name: '',
      },
    })

    expect(screen.getByText('COLLEGE Rouen')).toBeInTheDocument()
    expect(screen.getByText('76000')).toBeInTheDocument()
  })

  it('should display "-" for Offer when institution name and postal code are empty', () => {
    props.educationalInstitution.name = ''
    props.educationalInstitution.postalCode = ''
    props.educationalInstitution.institutionType = ''
    props.educationalInstitution.city = ''

    renderOfferInstitutionCell(props)

    expect(screen.getByText('-')).toBeInTheDocument()
  })
})
