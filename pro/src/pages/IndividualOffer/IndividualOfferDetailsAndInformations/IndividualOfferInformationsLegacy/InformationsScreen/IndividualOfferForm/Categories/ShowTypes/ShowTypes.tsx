import { useFormikContext } from 'formik'

import { showOptionsTree } from 'commons/core/Offers/categoriesSubTypes'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { IndividualOfferFormValues } from 'pages/IndividualOffer/commons/types'
import { buildShowSubTypeOptions } from 'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferDetails/commons/utils/utils'
import { FORM_DEFAULT_VALUES } from 'pages/IndividualOffer/IndividualOfferDetailsAndInformations/IndividualOfferInformationsLegacy/InformationsScreen/IndividualOfferForm/commons/constants'
import { Select } from 'ui-kit/form/Select/Select'

interface ShowTypesProps {
  readOnly?: boolean
}

/* istanbul ignore next: DEBT, TO FIX */
export const ShowTypes = ({
  readOnly = false,
}: ShowTypesProps): JSX.Element => {
  const {
    values: { showType },
  } = useFormikContext<IndividualOfferFormValues>()

  const showTypesOptions = showOptionsTree
    .map((data) => ({
      label: data.label,
      value: data.code.toString(),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  const showSubTypeOptions = buildShowSubTypeOptions(showType)

  return (
    <>
      <FormLayout.Row>
        <Select
          label="Type de spectacle"
          name="showType"
          options={showTypesOptions}
          defaultOption={{
            label: 'Choisir un type de spectacle',
            value: FORM_DEFAULT_VALUES.showType,
          }}
          disabled={readOnly}
        />
      </FormLayout.Row>
      {showSubTypeOptions.length > 0 && (
        <FormLayout.Row>
          <Select
            label="Sous-type"
            name="showSubType"
            options={showSubTypeOptions}
            defaultOption={{
              label: 'Choisir un sous-type',
              value: FORM_DEFAULT_VALUES.showSubType,
            }}
            disabled={readOnly}
          />
        </FormLayout.Row>
      )}
    </>
  )
}
