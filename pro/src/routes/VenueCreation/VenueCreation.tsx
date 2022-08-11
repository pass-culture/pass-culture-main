import React from 'react'

import { setDefaultInitialFormValues } from 'new_components/VenueForm'
import { VenueEdition as VenueEditionScreen } from 'screens/VenueEdition'

const VenueCreation = (): JSX.Element => {
  const initialValues = setDefaultInitialFormValues()

  return <VenueEditionScreen initialValues={initialValues} />
}

export default VenueCreation
