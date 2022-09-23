import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { StudentLevels } from 'apiClient/v2'
import { buildStudentLevelsMapWithDefaultValue } from 'core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'

import FormParticipants from '../FormParticipants'
import { ALL_STUDENTS_LABEL } from '../participantsOptions'

const initialValues = {
  participants: {
    ...buildStudentLevelsMapWithDefaultValue(true),
    CAPAnnee2: false,
    all: false,
  },
}

describe('FormParticipants', () => {
  it('should render all options with default value', async () => {
    render(
      <Formik initialValues={initialValues} onSubmit={() => {}}>
        <FormParticipants disableForm={false} />
      </Formik>
    )
    expect(await screen.findAllByRole('checkbox')).toHaveLength(8)
    expect(
      screen.getByRole('checkbox', { name: StudentLevels.LYC_E_PREMI_RE })
    ).toBeChecked()
  })

  describe('useParticipantUpdates', () => {
    it('should set all participants to true when user selects "all"', async () => {
      const initialValues = {
        participants: {
          ...buildStudentLevelsMapWithDefaultValue(false),
          all: false,
        },
      }

      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <FormParticipants disableForm={false} />
        </Formik>
      )
      const allStudentsCheckbox = screen.getByRole('checkbox', {
        name: ALL_STUDENTS_LABEL,
      })

      await userEvent.click(allStudentsCheckbox)
      await waitFor(() =>
        expect(screen.getByLabelText(ALL_STUDENTS_LABEL)).toBeChecked()
      )
      Object.values(StudentLevels).forEach(studentLevel => {
        const studentLevelCheckbox = screen.getByRole('checkbox', {
          name: studentLevel,
        })
        expect(studentLevelCheckbox).toBeChecked()
      })
    })

    it('should set all participants to false when user unselects "all"', async () => {
      const initialValues = {
        participants: {
          ...buildStudentLevelsMapWithDefaultValue(true),
          all: true,
        },
      }

      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <FormParticipants disableForm={false} />
        </Formik>
      )
      const allStudentsCheckbox = screen.getByRole('checkbox', {
        name: ALL_STUDENTS_LABEL,
      })

      await userEvent.click(allStudentsCheckbox)
      await waitFor(() =>
        expect(screen.getByLabelText(ALL_STUDENTS_LABEL)).not.toBeChecked()
      )
      Object.values(StudentLevels).forEach(studentLevel => {
        const studentLevelCheckbox = screen.getByRole('checkbox', {
          name: studentLevel,
        })
        expect(studentLevelCheckbox).not.toBeChecked()
      })
    })

    it('should select "all" when user selects all participants', async () => {
      const initialValues = {
        participants: {
          ...buildStudentLevelsMapWithDefaultValue(true),
          [StudentLevels.CAP_2E_ANN_E]: false,
          all: false,
        },
      }

      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <FormParticipants disableForm={false} />
        </Formik>
      )
      const allStudentsCheckbox = screen.getByRole('checkbox', {
        name: ALL_STUDENTS_LABEL,
      })

      await userEvent.click(allStudentsCheckbox)
      await waitFor(() =>
        expect(screen.getByLabelText(ALL_STUDENTS_LABEL)).toBeChecked()
      )
      Object.values(StudentLevels).forEach(studentLevel => {
        const studentLevelCheckbox = screen.getByRole('checkbox', {
          name: studentLevel,
        })
        expect(studentLevelCheckbox).toBeChecked()
      })
    })

    it('should unselect "all" when user deselects one participant', async () => {
      const initialValues = {
        participants: {
          ...buildStudentLevelsMapWithDefaultValue(true),
          all: true,
        },
      }

      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <FormParticipants disableForm={false} />
        </Formik>
      )
      const quatriemeCheckbox = screen.getByRole('checkbox', {
        name: StudentLevels.COLL_GE_4E,
      })

      await userEvent.click(quatriemeCheckbox)
      await waitFor(() =>
        expect(
          screen.getByLabelText(StudentLevels.COLL_GE_4E)
        ).not.toBeChecked()
      )
      Object.values(StudentLevels)
        .filter(studentLevel => studentLevel !== StudentLevels.COLL_GE_4E)
        .forEach(studentLevel => {
          const studentLevelCheckbox = screen.getByRole('checkbox', {
            name: studentLevel,
          })
          expect(studentLevelCheckbox).toBeChecked()
        })
      expect(screen.getByLabelText(ALL_STUDENTS_LABEL)).not.toBeChecked()
    })

    it('should not change "all"', async () => {
      const initialValues = {
        participants: {
          ...buildStudentLevelsMapWithDefaultValue(false),
          [StudentLevels.COLL_GE_4E]: true,
          [StudentLevels.COLL_GE_3E]: true,
          all: false,
        },
      }

      render(
        <Formik initialValues={initialValues} onSubmit={() => {}}>
          <FormParticipants disableForm={false} />
        </Formik>
      )
      const secondeCheckbox = screen.getByRole('checkbox', {
        name: StudentLevels.LYC_E_SECONDE,
      })

      await userEvent.click(secondeCheckbox)
      await waitFor(() =>
        expect(screen.getByLabelText(StudentLevels.LYC_E_SECONDE)).toBeChecked()
      )
      expect(
        screen.getByLabelText(StudentLevels.CAP_1RE_ANN_E)
      ).not.toBeChecked()
      expect(screen.getByLabelText(ALL_STUDENTS_LABEL)).not.toBeChecked()
    })
  })
})
