import { FormLayout } from 'components/FormLayout/FormLayout'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

export interface ExternalLinkProps {
  readOnlyFields?: string[]
}

export const ExternalLink = ({
  readOnlyFields,
}: ExternalLinkProps): JSX.Element => {
  return (
    <FormLayout.Section title="Lien pour le grand public">
      <FormLayout.Row
        sideComponent={
          <InfoBox>
            Ce lien sera affiché au public souhaitant réserver l’offre mais ne
            disposant pas ou plus de crédit sur l’application.
          </InfoBox>
        }
      >
        <TextInput
          label="URL de votre site ou billetterie"
          name="externalTicketOfficeUrl"
          isOptional
          type="text"
          description="Format : https://exemple.com"
          disabled={readOnlyFields?.includes('externalTicketOfficeUrl')}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}
