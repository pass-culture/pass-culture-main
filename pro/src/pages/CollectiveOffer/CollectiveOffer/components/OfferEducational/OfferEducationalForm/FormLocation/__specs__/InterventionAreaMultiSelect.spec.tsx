import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'

import { mainlandOptions } from 'commons/core/shared/interventionOptions'

import { InterventionAreaMultiSelect } from '../InterventionAreaMultiSelect'

describe('InterventionAreaMultiSelect', () => {
  it('should render correctly', () => {
    render(
      <Formik
        initialValues={{ interventionArea: ['75', '44'] }}
        onSubmit={() => {}}
      >
        <InterventionAreaMultiSelect
          label="sélectionnez des départements"
          disabled={false}
        />
      </Formik>
    )

    expect(screen.getByText('sélectionnez des départements *'))
    expect(screen.getByText('2'))
    expect(screen.getByText('Département(s)'))
    expect(screen.getByText('44 - Loire-Atlantique'))
    expect(screen.getByText('75 - Paris'))
  })

  it('should check all mainland departments when checking mainland', async () => {
    render(
      <Formik initialValues={{ interventionArea: [] }} onSubmit={() => {}}>
        <InterventionAreaMultiSelect
          label="sélectionnez des départements"
          disabled={false}
        />
      </Formik>
    )

    const departmentButton = screen.getByLabelText('Département(s)')
    await userEvent.click(departmentButton)

    const mainlandCheckbox = screen.getByLabelText('France métropolitaine')
    await userEvent.click(mainlandCheckbox)

    expect(mainlandCheckbox).toBeChecked()

    mainlandOptions.forEach((departmentOption) => {
      const departmentCheckbox = screen.getByLabelText(departmentOption.label)
      expect(departmentCheckbox).toBeChecked()
    })
  })

  it('should uncheck mainland option when a department is unchecked', async () => {
    render(
      <Formik
        initialValues={{
          interventionArea: [
            ...mainlandOptions.map((value) => value.id),
            'mainland',
          ],
        }}
        onSubmit={() => {}}
      >
        <InterventionAreaMultiSelect
          label="sélectionnez des départements"
          disabled={false}
        />
      </Formik>
    )

    const departmentButton = screen.getByLabelText('Département(s)')
    await userEvent.click(departmentButton)

    const mainlandCheckbox = screen.getByLabelText('France métropolitaine')
    expect(mainlandCheckbox).toBeChecked()

    const parisCheckbox = screen.getByLabelText('75 - Paris')
    await userEvent.click(parisCheckbox)

    expect(mainlandCheckbox).not.toBeChecked()
  })
})
