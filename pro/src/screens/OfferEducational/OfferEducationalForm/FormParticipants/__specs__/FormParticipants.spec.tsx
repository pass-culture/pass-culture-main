import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import {
  GetCollectiveOfferCollectiveStockResponseModel,
  StudentLevels,
} from 'apiClient/v1'
import { buildStudentLevelsMapWithDefaultValue } from 'core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'
import { RootState } from 'store/reducers'
import { collectiveStockFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import FormParticipants from '../FormParticipants'
import { ALL_STUDENTS_LABEL } from '../useParticipantsOptions'

const filteredParticipants = Object.values(StudentLevels).filter(
  studentLevel =>
    studentLevel !== StudentLevels.COLL_GE_6E &&
    studentLevel !== StudentLevels.COLL_GE_5E
)

const renderFormParticipants = (
  participants: Record<string, boolean>,
  storeOverride?: Partial<RootState>,
  offerStock?: GetCollectiveOfferCollectiveStockResponseModel | null
) => {
  const storeOverrides = {
    features: {
      initialized: true,
      list: [
        {
          isActive: false,
          nameKey: 'WIP_ADD_CLG_6_5_COLLECTIVE_OFFER',
        },
      ],
    },
    ...storeOverride,
  }
  return renderWithProviders(
    <Formik initialValues={{ participants }} onSubmit={() => {}}>
      <FormParticipants disableForm={false} offerStock={offerStock} />
    </Formik>,
    { storeOverrides }
  )
}

describe('FormParticipants', () => {
  let participants: Record<string, boolean> = {
    ...buildStudentLevelsMapWithDefaultValue(true),
    CAPAnnee2: false,
    all: false,
  }
  it('should render all options with default value', async () => {
    renderFormParticipants(participants)
    expect(await screen.findAllByRole('checkbox')).toHaveLength(8)
    expect(
      screen.getByRole('checkbox', { name: StudentLevels.LYC_E_PREMI_RE })
    ).toBeChecked()
  })

  describe('useParticipantUpdates', () => {
    it('should set all participants to true when user selects "all"', async () => {
      participants = {
        ...buildStudentLevelsMapWithDefaultValue(false),
        all: false,
      }
      renderFormParticipants(participants)
      const allStudentsCheckbox = screen.getByRole('checkbox', {
        name: ALL_STUDENTS_LABEL,
      })

      await userEvent.click(allStudentsCheckbox)
      await waitFor(() =>
        expect(screen.getByLabelText(ALL_STUDENTS_LABEL)).toBeChecked()
      )
      filteredParticipants.forEach(studentLevel => {
        const studentLevelCheckbox = screen.getByRole('checkbox', {
          name: studentLevel,
        })
        expect(studentLevelCheckbox).toBeChecked()
      })
    })

    it('should set all participants to false when user unselects "all"', async () => {
      participants = {
        ...buildStudentLevelsMapWithDefaultValue(true),
        all: true,
      }
      renderFormParticipants(participants)
      const allStudentsCheckbox = screen.getByRole('checkbox', {
        name: ALL_STUDENTS_LABEL,
      })

      await userEvent.click(allStudentsCheckbox)
      await waitFor(() =>
        expect(screen.getByLabelText(ALL_STUDENTS_LABEL)).not.toBeChecked()
      )
      filteredParticipants.forEach(studentLevel => {
        const studentLevelCheckbox = screen.getByRole('checkbox', {
          name: studentLevel,
        })
        expect(studentLevelCheckbox).not.toBeChecked()
      })
    })

    it('should select "all" when user selects all participants', async () => {
      participants = {
        ...buildStudentLevelsMapWithDefaultValue(true),
        [StudentLevels.CAP_2E_ANN_E]: false,
        all: false,
      }
      renderFormParticipants(participants)

      const allStudentsCheckbox = screen.getByRole('checkbox', {
        name: ALL_STUDENTS_LABEL,
      })

      await userEvent.click(allStudentsCheckbox)
      await waitFor(() =>
        expect(screen.getByLabelText(ALL_STUDENTS_LABEL)).toBeChecked()
      )
      filteredParticipants.forEach(studentLevel => {
        const studentLevelCheckbox = screen.getByRole('checkbox', {
          name: studentLevel,
        })
        expect(studentLevelCheckbox).toBeChecked()
      })
    })

    it('should unselect "all" when user deselects one participant', async () => {
      participants = {
        ...buildStudentLevelsMapWithDefaultValue(true),
        all: true,
      }
      renderFormParticipants(participants)

      const quatriemeCheckbox = screen.getByRole('checkbox', {
        name: StudentLevels.COLL_GE_4E,
      })

      await userEvent.click(quatriemeCheckbox)
      await waitFor(() =>
        expect(
          screen.getByLabelText(StudentLevels.COLL_GE_4E)
        ).not.toBeChecked()
      )
      filteredParticipants
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
      participants = {
        ...buildStudentLevelsMapWithDefaultValue(false),
        [StudentLevels.COLL_GE_4E]: true,
        [StudentLevels.COLL_GE_3E]: true,
        all: false,
      }
      renderFormParticipants(participants)

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

    it('should display clg 6 & 5 if ff active', () => {
      const storeOverride = {
        features: {
          initialized: true,
          list: [
            {
              isActive: true,
              nameKey: 'WIP_ADD_CLG_6_5_COLLECTIVE_OFFER',
            },
          ],
        },
      }
      renderFormParticipants(participants, storeOverride)

      expect(
        screen.getByLabelText(
          `${StudentLevels.COLL_GE_6E} : à partir de septembre 2023`
        )
      ).toBeInTheDocument()
      expect(
        screen.getByLabelText(
          `${StudentLevels.COLL_GE_5E} : à partir de septembre 2023`
        )
      ).toBeInTheDocument()
    })

    it('should not display clg 6 & 5 if stock exist before 1st september', () => {
      const storeOverride = {
        features: {
          initialized: true,
          list: [
            {
              isActive: true,
              nameKey: 'WIP_ADD_CLG_6_5_COLLECTIVE_OFFER',
            },
          ],
        },
      }
      const offerStock = collectiveStockFactory()
      renderFormParticipants(participants, storeOverride, offerStock)

      expect(
        screen.queryByLabelText(StudentLevels.COLL_GE_6E)
      ).not.toBeInTheDocument()
      expect(
        screen.queryByLabelText(StudentLevels.COLL_GE_5E)
      ).not.toBeInTheDocument()
    })
  })
})
