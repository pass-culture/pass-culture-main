import { render, screen } from '@testing-library/react'

import { BeneficiaryCell, BeneficiaryCellProps } from '../BeneficiaryCell'

const renderBeneficiaryCell = (props: BeneficiaryCellProps) =>
  render(<BeneficiaryCell {...props} />)

describe('BeneficiaryCell', () => {
  it('should display an user firstname, lastname and email address', () => {
    const props = {
      beneficiaryInfos: {
        firstname: 'Laurent',
        lastname: 'Durond',
        email: 'laurentdurond@example.com',
      },
    }

    renderBeneficiaryCell(props)

    expect(screen.getByText('Durond Laurent')).toBeInTheDocument()
    expect(screen.getByText('laurentdurond@example.com')).toBeInTheDocument()
  })

  it.each`
    firstName | lastName    | expectedResult
    ${'Reda'} | ${'Khteur'} | ${'Khteur Reda'}
    ${'Reda'} | ${null}     | ${'Reda'}
    ${null}   | ${'Khteur'} | ${'Khteur'}
  `(
    'should display the right formatted user name',
    ({ firstName, lastName, expectedResult }) => {
      const props = {
        beneficiaryInfos: {
          firstname: firstName,
          lastname: lastName,
          email: 'laurentdurond@example.com',
        },
      }
      renderBeneficiaryCell(props)

      expect(screen.getByText(expectedResult)).toBeInTheDocument()
    }
  )

  it('should not display beneficiary name part when no first nor last name is given', () => {
    const props = {
      beneficiaryInfos: {
        firstname: null,
        lastname: null,
        email: 'laurentdurond@example.com',
      },
    }

    renderBeneficiaryCell(props)

    expect(
      screen.queryByTestId('booking-cell-beneficiary-name')
    ).not.toBeInTheDocument()
  })
})
