import { StudentLevels } from 'apiClient/adage'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { CheckboxGroup } from 'ui-kit/form/CheckboxGroup/CheckboxGroup'
import { CheckboxVariant } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

const studentLevelsLabels = {
  [StudentLevels._COLES_MARSEILLE_MATERNELLE]: 'Maternelle',
  [StudentLevels._COLES_MARSEILLE_CP_CE1_CE2]: 'CP, CE1, CE2',
  [StudentLevels._COLES_MARSEILLE_CM1_CM2]: 'CM1, CM2',
  [StudentLevels.COLL_GE_6E]: '6e',
  [StudentLevels.COLL_GE_5E]: '5e',
  [StudentLevels.COLL_GE_4E]: '4e',
  [StudentLevels.COLL_GE_3E]: '3e',
  [StudentLevels.CAP_1RE_ANN_E]: 'CAP - 1re année',
  [StudentLevels.CAP_2E_ANN_E]: 'CAP - 2e année',
  [StudentLevels.LYC_E_SECONDE]: 'Seconde',
  [StudentLevels.LYC_E_PREMI_RE]: 'Première',
  [StudentLevels.LYC_E_TERMINALE]: 'Terminale',
}

export const FormParticipants = ({
  disableForm,
}: {
  disableForm: boolean
  isTemplate: boolean
}): JSX.Element => {
  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')

  const defaultPartipantsOptions = Object.values(StudentLevels).map(
    (studentLevel) => ({
      label: studentLevelsLabels[studentLevel],
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
                  variant={CheckboxVariant.BOX}
                  group={filteredParticipantsOptions.filter((option) =>
                    option.name.startsWith('participants.Collège')
                  )}
                  groupName="college"
                  disabled={disableForm}
                  describedBy="Niveau du collège"
                  inline={true}
                />
              ),
            },
            {
              name: 'lycee',
              label: 'Lycée',
              childrenOnChecked: (
                <CheckboxGroup
                  variant={CheckboxVariant.BOX}
                  group={filteredParticipantsOptions.filter(
                    (option) =>
                      option.name.startsWith('participants.CAP') ||
                      option.name.startsWith('participants.Lycée')
                  )}
                  groupName="lycee"
                  disabled={disableForm}
                  describedBy="Niveau du lycée"
                  inline={true}
                />
              ),
            },
            {
              name: 'marseille',
              label: 'Projet Marseille en Grand - École innovante',
              childrenOnChecked: (
                <CheckboxGroup
                  variant={CheckboxVariant.BOX}
                  group={filteredParticipantsOptions.filter((option) =>
                    option.name.startsWith('participants.Écoles Marseille')
                  )}
                  groupName="marseille"
                  disabled={disableForm}
                  describedBy="Niveau du projet Marseille en Grand - École innovante"
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
