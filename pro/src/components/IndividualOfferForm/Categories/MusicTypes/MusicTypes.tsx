import { FormLayout } from 'components/FormLayout/FormLayout'
import { FORM_DEFAULT_VALUES } from 'components/IndividualOfferForm'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { Select } from 'ui-kit/form/Select/Select'

interface MusicTypesProps {
  readOnly?: boolean
  isEvent: boolean | null
}

const MusicTypes = ({
  readOnly = false,
  isEvent = false,
}: MusicTypesProps): JSX.Element => {
  const { musicTypes } = useIndividualOfferContext()

  return (
    <FormLayout.Row>
      <Select
        label="Genre musical"
        name="gtl_id"
        options={(isEvent
          ? musicTypes.filter((musicType) => musicType.canBeEvent)
          : musicTypes
        ).map((data) => ({
          value: data.gtl_id,
          label: data.label,
        }))}
        defaultOption={{
          label: 'Choisir un genre musical',
          value: FORM_DEFAULT_VALUES.gtl_id,
        }}
        disabled={readOnly}
      />
    </FormLayout.Row>
  )
}

export default MusicTypes
