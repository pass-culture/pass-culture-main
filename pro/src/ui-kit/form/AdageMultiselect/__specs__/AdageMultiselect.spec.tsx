import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import AdageMultiselect from '../AdageMultiselect'

const options = [
  { value: 1, label: 'Architecture' },
  { value: 2, label: 'Danse' },
  { value: 3, label: 'Théatre' },
]

const renderAdageMultiselect = (
  initialValues: (number | string | string[])[] = [],
  customOptions: {
    value: number | string | string[]
    label: string
  }[] = options
) => {
  render(
    <Formik
      initialValues={{ educationalDomains: initialValues }}
      onSubmit={() => {}}
    >
      <AdageMultiselect
        options={customOptions}
        placeholder="Ex: Théâtre"
        name="educationalDomains"
        label="Rechercher un domaine artistique"
        isOpen={true}
      />
    </Formik>
  )
}

describe('AdageMultiselect', () => {
  it('should filter options when user type in input', async () => {
    renderAdageMultiselect()

    const input = screen.getByPlaceholderText('Ex: Théâtre')
    await userEvent.type(input, 'Th')

    expect(screen.getByText('Théatre')).toBeInTheDocument()
    expect(screen.queryByText('Architecture')).not.toBeInTheDocument()
    expect(screen.queryByText('Danse')).not.toBeInTheDocument()
  })
  it('should check an option when user click on it', async () => {
    renderAdageMultiselect()

    const option = screen.getByText('Danse')
    await userEvent.click(option)

    expect(screen.getByLabelText('Danse')).toBeChecked()
  })

  it('should uncheck an option when user click on it', async () => {
    renderAdageMultiselect([2])

    const option = screen.getByText('Danse')
    await userEvent.click(option)

    expect(screen.getByLabelText('Danse')).not.toBeChecked()

    await userEvent.click(option)

    expect(screen.getByLabelText('Danse')).toBeChecked()
  })

  it('should display all options when user erase input value', async () => {
    renderAdageMultiselect()

    const input = screen.getByPlaceholderText('Ex: Théâtre')

    await userEvent.type(input, 'Th')

    expect(screen.getByText('Théatre')).toBeInTheDocument()
    expect(screen.queryByText('Architecture')).not.toBeInTheDocument()
    expect(screen.queryByText('Danse')).not.toBeInTheDocument()

    await userEvent.clear(input)

    expect(screen.getByText('Théatre')).toBeInTheDocument()
    expect(screen.getByText('Architecture')).toBeInTheDocument()
    expect(screen.getByText('Danse')).toBeInTheDocument()
  })

  it('should have the correct options checked when values are string[]', async () => {
    const strArrayOptions = [
      {
        value: ['val1', 'val2'],
        label: 'label1',
      },
      {
        value: ['val3'],
        label: 'label2',
      },
    ]

    renderAdageMultiselect([['val3']], strArrayOptions)

    expect(screen.getByLabelText('label2')).toBeChecked()
    expect(screen.getByLabelText('label1')).not.toBeChecked()
  })
})
