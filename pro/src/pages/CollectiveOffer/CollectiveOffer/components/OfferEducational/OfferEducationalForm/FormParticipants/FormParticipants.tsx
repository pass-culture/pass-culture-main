import { StudentLevels } from 'apiClient/adage'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { CheckboxVariant } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

export const FormParticipants = ({
  disableForm,
}: {
  disableForm: boolean
  isTemplate: boolean
}): JSX.Element => {
  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const defaultPartipantsOptions = Object.values(StudentLevels).map(
    (studentLevel) => ({
      label: studentLevel,
      name: `participants.${studentLevel}`,
    })
  )

  const filteredParticipantsOptions = isMarseilleEnabled
    ? defaultPartipantsOptions
    : defaultPartipantsOptions.filter(
        (option) =>
          option.name !==
            `participants.${StudentLevels._COLES_MARSEILLE_MATERNELLE}` &&
          option.name !==
            `participants.${StudentLevels._COLES_MARSEILLE_CP_CE1_CE2}` &&
          option.name !==
            `participants.${StudentLevels._COLES_MARSEILLE_CM1_CM2}`
      )

  return (
    <FormLayout.Section title="À quels niveaux scolaires s’adressent votre offre ?">
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
          group={filteredParticipantsOptions}
          groupName="participants"
          legend="Cette offre s'adresse aux élèves de :"
          disabled={disableForm}
        />

        <CheckboxGroup
          groupName="participants"
          variant={CheckboxVariant.BOX}
          legend="Cette offre s'adresse aux élèves de :"
          disabled={disableForm}
          group={[
            {
              name: 'college',
              label: 'Collège',
              childrenOnChecked: (
                <CheckboxGroup
                  group={filteredParticipantsOptions.filter((option) =>
                    option.label.startsWith('Collège')
                  )}
                  groupName="college"
                  disabled={disableForm}
                  legend="Niveau du collège"
                  inline={true}
                />
              ),
            },
          ]}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
