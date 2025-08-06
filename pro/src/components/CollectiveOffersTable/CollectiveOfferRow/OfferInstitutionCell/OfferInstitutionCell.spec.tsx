import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferInstitutionCell,
  OfferInstitutionCellProps,
} from './OfferInstitutionCell'

const props = {
  rowId: 'offer-row-1',
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
    <>
      <table>
        <tbody>
          <tr>
            <OfferInstitutionCell {...props} />
          </tr>
        </tbody>
      </table>
    </>
  )

describe('OfferInstitutionCell', () => {
  it('should display the full institution name when provided', () => {
    renderOfferInstitutionCell(props)

    expect(screen.getByRole('cell')).toHaveTextContent('Collège Bellevue')
  })

  it('should display institutionType and city when name is not provided', () => {
    props.educationalInstitution.name = ''

    renderOfferInstitutionCell(props)

    expect(screen.getByRole('cell')).toHaveTextContent('COLLEGE Rouen')
  })

  it('should display "Tous les établissements" when institution type and city are empty', () => {
    props.educationalInstitution.institutionType = ''
    props.educationalInstitution.city = ''

    renderOfferInstitutionCell(props)

    expect(screen.getByRole('cell')).toHaveTextContent(
      'Tous les établissements'
    )
  })

  it('should include custom class and headers attribute', () => {
    props.rowId = 'row-42'
    props.className = 'my-custom'

    renderOfferInstitutionCell(props)

    const cell = screen.getByRole('cell')
    expect(cell).toHaveClass('my-custom')
    expect(cell.getAttribute('headers')).toContain('row-42')
  })
})
