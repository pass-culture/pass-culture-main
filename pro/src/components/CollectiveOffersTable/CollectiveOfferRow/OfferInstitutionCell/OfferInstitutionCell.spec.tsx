import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferInstitutionCell,
  type OfferInstitutionCellProps,
} from './OfferInstitutionCell'

const props = {
  rowId: 'offer-row-1',
  isTemplate: true,
  className: 'custom-class',
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
  renderWithProviders(
    <table>
        <tbody>
          <tr>
            <OfferInstitutionCell {...props} />
          </tr>
        </tbody>
      </table>
  )

describe('OfferInstitutionCell', () => {
  it('should display the full institution name and postal code when provided', () => {
    renderOfferInstitutionCell({
      ...props,
      educationalInstitution: {
        ...props.educationalInstitution,
        postalCode: '76000',
      },
    })

    expect(screen.getByRole('cell')).toHaveTextContent(
      'Collège Bellevue - 76000'
    )
  })

  it('should display institutionType and city when name is not provided', () => {
    renderOfferInstitutionCell({
      ...props,
      educationalInstitution: {
        ...props.educationalInstitution,
        name: '',
      },
    })

    expect(screen.getByRole('cell')).toHaveTextContent('COLLEGE Rouen')
  })

  it('should display "Tous les établissements" for OfferTemplate when institution name and postal code are empty', () => {
    renderOfferInstitutionCell({
      ...props,
      educationalInstitution: {
        ...props.educationalInstitution,
        postalCode: '',
        name: '',
        institutionType: '',
        city: '',
      },
    })

    expect(screen.getByRole('cell')).toHaveTextContent(
      'Tous les établissements'
    )
  })

  it('should display "-" for Offer when institution name and postal code are empty', () => {
    props.educationalInstitution.name = ''
    props.educationalInstitution.postalCode = ''
    props.educationalInstitution.institutionType = ''
    props.educationalInstitution.city = ''
    props.isTemplate = false

    renderOfferInstitutionCell(props)

    expect(screen.getByRole('cell')).toHaveTextContent('-')
  })

  it('should include custom class and headers attribute', () => {
    renderOfferInstitutionCell({
      ...props,
      rowId: 'row-42',
      className: 'my-custom',
    })

    const cell = screen.getByRole('cell')
    expect(cell).toHaveClass('my-custom')
    expect(cell.getAttribute('headers')).toContain('row-42')
  })
})
