import { useFormikContext } from 'formik'
import { ChangeEvent, useEffect, useId, useState } from 'react'

import { StudentLevels } from 'apiClient/adage'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { CheckboxVariant } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { studentLevelsLabels } from './constants'
import styles from './FormParticipants.module.scss'

const levelGroups = {
  college: [
    StudentLevels.COLL_GE_6E,
    StudentLevels.COLL_GE_5E,
    StudentLevels.COLL_GE_4E,
    StudentLevels.COLL_GE_3E,
  ],
  lycee: [
    StudentLevels.LYC_E_SECONDE,
    StudentLevels.LYC_E_PREMI_RE,
    StudentLevels.LYC_E_TERMINALE,
    StudentLevels.CAP_1RE_ANN_E,
    StudentLevels.CAP_2E_ANN_E,
  ],
  marseille: [
    StudentLevels._COLES_MARSEILLE_MATERNELLE,
    StudentLevels._COLES_MARSEILLE_CP_CE1_CE2,
    StudentLevels._COLES_MARSEILLE_CM1_CM2,
  ],
}

type LevelGroup = keyof typeof levelGroups

export const FormParticipants = ({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element => {
  const isMarseilleEnabled = useActiveFeature('ENABLE_MARSEILLE')
  const { setFieldValue, values } =
    useFormikContext<OfferEducationalFormValues>()
  const [checkboxesState, setCheckboxesState] = useState({
    college: false,
    lycee: false,
    marseille: false,
  })
  const collegeLabelId = useId()
  const lyceeLabelId = useId()
  const marseilleLabelId = useId()

  const updateLevelGroupState = async (group: LevelGroup) => {
    const levels = levelGroups[group]
    const checkedLevels = levels.filter(
      (level) => values.participants[level]
    ).length

    await setFieldValue(
      `participants.${group}`,
      checkedLevels === levels.length
    )
    const isPartiallyChecked =
      checkedLevels > 0 && checkedLevels < levels.length
    setCheckboxesState((prevState) => ({
      ...prevState,
      [group]: isPartiallyChecked,
    }))
  }

  useEffect(() => {
    Object.keys(levelGroups).forEach((group) => {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      updateLevelGroupState(group as LevelGroup)
    })
  }, [values.participants])

  const defaultPartipantsOptions = Object.values(StudentLevels).map(
    (studentLevel) => ({
      label: studentLevelsLabels[studentLevel],
      name: `participants.${studentLevel}`,
    })
  )

  const handleLevelChange = async (level: LevelGroup, checked: boolean) => {
    for (const studentLevel of levelGroups[level]) {
      await setFieldValue(`participants.${studentLevel}`, checked)
    }
  }

  const handleChildCheckboxChange = async (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const { name, checked } = event.target

    await setFieldValue(name, checked)

    if (!checked) {
      if (name.startsWith('participants.Collège')) {
        await setFieldValue('participants.college', false)
      } else if (
        name.startsWith('participants.Lycée') ||
        name.startsWith('participants.CAP')
      ) {
        await setFieldValue('participants.lycee', false)
      } else if (name.startsWith('participants.Écoles Marseille')) {
        await setFieldValue('participants.marseille', false)
      }
    }
  }

  const collegeLyceeOptions = [
    {
      name: 'participants.college',
      label: <span id={collegeLabelId}>Collège</span>,
      onChange: (event: ChangeEvent<HTMLInputElement>) =>
        handleLevelChange('college', event.target.checked),
      childrenOnChecked: (
        <CheckboxGroup
          variant={CheckboxVariant.BOX}
          group={defaultPartipantsOptions
            .filter((option) => option.name.startsWith('participants.Collège'))
            .map((option) => ({
              ...option,
              onChange: handleChildCheckboxChange,
            }))}
          groupName="participants.college"
          disabled={disableForm}
          describedBy={collegeLabelId}
          inline={true}
        />
      ),
      shouldShowChildren: checkboxesState.college,
    },
    {
      name: 'participants.lycee',
      label: <span id={lyceeLabelId}>Lycée</span>,
      onChange: (event: ChangeEvent<HTMLInputElement>) =>
        handleLevelChange('lycee', event.target.checked),
      childrenOnChecked: (
        <CheckboxGroup
          variant={CheckboxVariant.BOX}
          group={defaultPartipantsOptions.filter(
            (option) =>
              option.name.startsWith('participants.CAP') ||
              option.name.startsWith('participants.Lycée')
          )}
          groupName="participants.lycee"
          disabled={disableForm}
          describedBy={lyceeLabelId}
          inline={true}
        />
      ),
      shouldShowChildren: checkboxesState.lycee,
    },
  ]

  const marseilleOption = {
    name: 'participants.marseille',
    label: (
      <span id={marseilleLabelId}>
        Projet Marseille en Grand - École innovante
      </span>
    ),
    onChange: (event: ChangeEvent<HTMLInputElement>) =>
      handleLevelChange('marseille', event.target.checked),
    childrenOnChecked: (
      <CheckboxGroup
        variant={CheckboxVariant.BOX}
        group={defaultPartipantsOptions.filter((option) =>
          option.name.startsWith('participants.Écoles Marseille')
        )}
        groupName="participants.marseille"
        disabled={disableForm}
        describedBy={marseilleLabelId}
        inline={true}
      />
    ),
    shouldShowChildren: checkboxesState.marseille,
  }

  const studentLevelsOptions = isMarseilleEnabled
    ? [...collegeLyceeOptions, marseilleOption]
    : collegeLyceeOptions

  return (
    <div className={styles['container']}>
      <FormLayout.Row
        sideComponent={
          <InfoBox>
            {isMarseilleEnabled
              ? `Dans le cadre du plan Marseille en Grand et du Conseil national de la refondation dans son volet éducation "Notre école, faisons-la ensemble", les écoles primaires innovantes du territoire marseillais bénéficient d’un budget pour financer des projets d’EAC avec leurs élèves.`
              : `Le pass Culture à destination du public scolaire s’adresse aux
            élèves de la sixième à la terminale des établissements publics et
            privés sous contrat.`}
          </InfoBox>
        }
      >
        <CheckboxGroup
          groupName="participants"
          legend={
            <h2 className={styles['subtitle']}>
              À quels niveaux scolaires s’adressent votre offre ? *
            </h2>
          }
          hideAsterisk
          variant={CheckboxVariant.BOX}
          disabled={disableForm}
          group={studentLevelsOptions}
        />
      </FormLayout.Row>
    </div>
  )
}
