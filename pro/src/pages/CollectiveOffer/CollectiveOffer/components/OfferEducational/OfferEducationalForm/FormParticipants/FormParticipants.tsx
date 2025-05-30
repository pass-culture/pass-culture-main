import { useFormikContext } from 'formik'
import { ChangeEvent, useRef } from 'react'

import { StudentLevels } from 'apiClient/adage'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { CheckboxGroup } from 'ui-kit/formV2/CheckboxGroup/CheckboxGroup'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import { studentLevelsLabels } from './constants'
import styles from './FormParticipants.module.scss'

export const FormParticipants = ({
  disableForm,
}: {
  disableForm: boolean
}): JSX.Element => {
  const isMarseilleEnabled = useActiveFeature('ENABLE_MARSEILLE')
  const { setFieldValue, values, getFieldProps, getFieldMeta } =
    useFormikContext<OfferEducationalFormValues>()

  const collegeRef = useRef<HTMLInputElement>(null)
  const lyceeRef = useRef<HTMLInputElement>(null)
  const marseilleRef = useRef<HTMLInputElement>(null)

  const defaultPartipantsOptions = Object.values(StudentLevels).map(
    (studentLevel) => ({
      label: studentLevelsLabels[studentLevel],
      name: `participants.${studentLevel}`,
    })
  )

  const getCheckboxroupForLevel = (
    values: OfferEducationalFormValues,
    levelPrefixes: string[],
    levelLabel: string,
    ref: React.RefObject<HTMLInputElement>
  ) => {
    const levelValues = Object.keys(values.participants).filter((v) =>
      levelPrefixes.some((prefix) => v.startsWith(prefix))
    )

    const levelCheckedValues = Object.entries(values.participants)
      .filter(([key]) => levelPrefixes.some((prefix) => key.startsWith(prefix)))
      .filter(([, val]) => val)
      .map(([key]) => key)

    const partiallyChecked =
      levelCheckedValues.length > 0 &&
      levelCheckedValues.length < levelValues.length

    return {
      label: levelLabel,
      checked: levelCheckedValues.length > 0,
      indeterminate: partiallyChecked,
      ref: ref,
      onChange: (event: ChangeEvent<HTMLInputElement>) => {
        for (const level of levelValues) {
          // eslint-disable-next-line @typescript-eslint/no-floating-promises
          setFieldValue(`participants.${level}`, event.target.checked)
        }
      },
      collapsed: (
        <CheckboxGroup
          name={levelPrefixes.join('')}
          legend="Choisissez des niveaux scolaires"
          group={defaultPartipantsOptions
            .filter((option) =>
              levelPrefixes.some((prefix) =>
                option.name.startsWith(`participants.${prefix}`)
              )
            )
            .map((option) => {
              return {
                ...option,
                checked: getFieldProps(option.name).value,
                onChange: (e) => {
                  // eslint-disable-next-line @typescript-eslint/no-floating-promises
                  setFieldValue(option.name, e.target.checked)

                  if (!e.target.checked && levelCheckedValues.length === 1) {
                    //  Refocus the parent checkbox when the last checkbox of the group is unchecked
                    ref.current?.focus()
                  }
                },
              }
            })}
          disabled={disableForm}
          inline
        />
      ),
    }
  }

  const collegeGroup = getCheckboxroupForLevel(
    values,
    ['Collège'],
    'Collège',
    collegeRef
  )
  const lyceeGroup = getCheckboxroupForLevel(
    values,
    ['Lycée', 'CAP'],
    'Lycée',
    lyceeRef
  )
  const marseilleGroup = getCheckboxroupForLevel(
    values,
    ['Écoles Marseille'],
    'Projet Marseille en Grand - École innovante',
    marseilleRef
  )

  const studentLevelsOptions = isMarseilleEnabled
    ? [collegeGroup, lyceeGroup, marseilleGroup]
    : [collegeGroup, lyceeGroup]

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
          legend={
            <h2 className={styles['subtitle']}>
              À quels niveaux scolaires s’adressent votre offre ? *
            </h2>
          }
          name="participants"
          disabled={disableForm}
          group={studentLevelsOptions}
          error={
            getFieldMeta('participants').touched
              ? getFieldMeta('participants').error
              : undefined
          }
        />
      </FormLayout.Row>
    </div>
  )
}
