import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import BeneficiaryCell from '../BeneficiaryCell'

const renderBeneficiaryCell = props => render(<BeneficiaryCell {...props} />)

describe('bookings beneficiary cell', () => {
  it('should display an user firstname, lastname and email address', () => {
    // Given
    const props = {
      beneficiaryInfos: {
        firstname: 'Laurent',
        lastname: 'Durond',
        email: 'laurentdurond@example.com',
      },
    }

    // When
    renderBeneficiaryCell(props)

    // Then
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
      // Given
      const props = {
        beneficiaryInfos: {
          firstname: firstName,
          lastname: lastName,
          email: 'laurentdurond@example.com',
        },
      }
      // When
      renderBeneficiaryCell(props)

      // Then
      expect(screen.getByText(expectedResult)).toBeInTheDocument()
    }
  )

  it('should not display beneficiary name part when no first nor last name is given', () => {
    // Given
    const props = {
      beneficiaryInfos: {
        firstname: null,
        lastname: null,
        email: 'laurentdurond@example.com',
      },
    }

    // When
    renderBeneficiaryCell(props)

    // Then
    expect(
      screen.queryByTestId('booking-cell-beneficiary-name')
    ).not.toBeInTheDocument()
  })
})
