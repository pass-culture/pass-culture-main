import useSWR from 'swr'

import { api } from 'apiClient/api'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { FORM_DEFAULT_VALUES } from 'components/IndividualOfferForm/constants'
import { GET_MUSIC_TYPES_QUERY_KEY } from 'config/swrQueryKeys'
import { Select } from 'ui-kit/form/Select/Select'

interface MusicTypesProps {
  readOnly?: boolean
  isEvent: boolean | null
}

export const MusicTypes = ({
  readOnly = false,
  isEvent = false,
}: MusicTypesProps): JSX.Element => {
  const musicTypesQuery = useSWR(
    GET_MUSIC_TYPES_QUERY_KEY,
    () => api.getMusicTypes(),
    { fallbackData: [] }
  )
  const musicTypes = musicTypesQuery.data

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
