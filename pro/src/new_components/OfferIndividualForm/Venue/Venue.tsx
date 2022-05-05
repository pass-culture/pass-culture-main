import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import FormLayout from 'new_components/FormLayout'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'
import { buildSelectOptions } from 'ui-kit/form/Select'
// import { Banner } from 'ui-kit'

export interface IVenueProps {
  offererNames: TOffererName[]
  venueList: TOfferIndividualVenue[]
}

const Venue = ({ offererNames, venueList }: IVenueProps): JSX.Element => {
  const { values } = useFormikContext<IOfferIndividualFormValues>()
  const [offererOptions, setOffererOptions] = useState<SelectOptions>([])
  const [venueOptions, setVenueOptions] = useState<SelectOptions>([])
  const [disabledFields, setDisabledField] = useState<{
    offererId: boolean
    venueId: boolean
  }>({ offererId: false, venueId: false })

  useEffect(() => {
    const newOptions = buildSelectOptions(
      offererNames,
      'name',
      'id',
      'Selectionner une structure'
    )
    setOffererOptions(newOptions)

    const disabledSelectOfferer = newOptions.length === 1
    setDisabledField(oldDisabledFields => ({
      ...oldDisabledFields,
      offererId: disabledSelectOfferer,
    }))
  }, [offererNames])

  useEffect(() => {
    const newOptions = buildSelectOptions(
      venueList.filter((venue: TOfferIndividualVenue) => {
        if (!values.offererId) {
          return false
        }
        return venue.managingOffererId === values.offererId
      }),
      'name',
      'id',
      'Selectionner un lieu'
    )
    setVenueOptions(newOptions)

    const disabledSelectVenue = !values.offererId || newOptions.length === 1
    setDisabledField(oldDisabledFields => ({
      ...oldDisabledFields,
      venueId: disabledSelectVenue,
    }))
  }, [values.offererId, venueList])

  // const displayNoRefundWarning =
  // values.subCategoryId && offerSubCategory.reimbursementRule === NOT_REIMBURSE

  return (
    <FormLayout.Section
      title="Informations pratiques"
      description="Les informations pratiques permettent de donner aux utilisateurs des informations sur le retrait de leur commande."
    >
      <Select
        disabled={disabledFields.offererId}
        label="Structure"
        name="offererId"
        options={offererOptions}
      />
      <Select
        disabled={disabledFields.venueId}
        label="Lieu"
        name="venueId"
        options={venueOptions}
      />

      {/*
        TODO (rlecellier): display : new_components/Banner/OfferRefundWarning
        when subCategory.reimbursementRule === NOT_REIMBURSE
       */}
    </FormLayout.Section>
  )
}

export default Venue
