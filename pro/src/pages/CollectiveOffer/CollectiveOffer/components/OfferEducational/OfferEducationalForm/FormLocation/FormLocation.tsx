import { useFormikContext } from 'formik'
import { useId } from 'react'

import {
  CollectiveLocationType,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { OfferEducationalFormValues } from 'commons/core/OfferEducational/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'

import styles from '../OfferEducationalForm.module.scss'

export interface FormLocationProps {
  venues?: VenueListItemResponseModel[]
  disableForm: boolean
}

export const FormLocation = ({
  venues,
  disableForm,
}: FormLocationProps): JSX.Element => {
  const specificAddressId = useId()
  const { values } = useFormikContext<OfferEducationalFormValues>()

  const selectedVenue = venues?.find(
    (v) => v.id.toString() === values.venueId.toString()
  )


  const addressTypeRadios = [
    {
      label: <span id={specificAddressId}>À une adresse précise</span>,
      value: CollectiveLocationType.ADDRESS,
      childrenOnChecked: (
        <RadioGroup
          describedBy={specificAddressId}
          variant={RadioVariant.BOX}
          group={[
            {
              label: (
                <span>
                  {selectedVenue &&
                    `${selectedVenue.address?.label} - ${selectedVenue.address?.street}
                  ${selectedVenue.address?.postalCode} ${selectedVenue.address?.city}`}
                </span>
              ),
              value: selectedVenue?.address?.id_oa.toString() ?? '',
            },
          ]}
          name={'location.id_oa'}
        />
      ),
    },
  ]

  return (
    <FormLayout.Row>
      <RadioGroup
        group={addressTypeRadios}
        legend={
          <h2 className={styles['subtitle']}>Où se déroule votre offre ?</h2>
        }
        name="location.locationType"
        variant={RadioVariant.BOX}
        disabled={disableForm}
      />
    </FormLayout.Row>
  )
}
