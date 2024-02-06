import React, { useEffect } from 'react'

import { api } from 'apiClient/api'
import { GetMusicTypesResponse } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { FORM_DEFAULT_VALUES } from 'components/IndividualOfferForm'
import { Select } from 'ui-kit'

interface MusicTypesProps {
  readOnly?: boolean
  isEvent: boolean | null
}

const MusicTypes = ({
  readOnly = false,
  isEvent = false,
}: MusicTypesProps): JSX.Element => {
  const [musicTypes, setMusicTypes] = React.useState<GetMusicTypesResponse>([])

  useEffect(() => {
    const getMusicTypes = async () => {
      const musicTypes = isEvent
        ? await api.getEventMusicTypes()
        : await api.getAllMusicTypes()
      setMusicTypes(musicTypes)
    }
    getMusicTypes() // eslint-disable-next-line @typescript-eslint/no-floating-promises
  }, [isEvent])

  return (
    <FormLayout.Row>
      <Select
        label="Genre musical"
        name="gtl_id"
        options={musicTypes.map((data) => ({
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
