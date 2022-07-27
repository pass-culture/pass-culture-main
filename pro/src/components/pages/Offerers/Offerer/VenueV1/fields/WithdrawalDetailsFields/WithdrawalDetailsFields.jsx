import PropTypes from 'prop-types'
import React, { useCallback } from 'react'
import { Field } from 'react-final-form'

import HiddenField from 'components/layout/form/fields/HiddenField'
import CheckboxInput from 'components/layout/inputs/CheckboxInput'
import TextareaInput from 'components/layout/inputs/TextareaInput'

const WithdrawalDetailsFields = props => {
  const { initialWithdrawalDetails, isCreatedEntity, readOnly } = props

  const renderWithdrawalDetails = useCallback(
    ({ input }) => {
      return (
        <TextareaInput
          {...input}
          countCharacters={!readOnly}
          disabled={readOnly}
          label=""
          maxLength={500}
          name="withdrawalDetails"
          rows={4}
          value={input.value}
        />
      )
    },
    [readOnly]
  )

  const renderIsAppliedWithdrawalOnAllOffers = useCallback(({ input }) => {
    return (
      <CheckboxInput
        {...input}
        label="Appliquer le changement à toutes les offres déjà existantes."
        name="isWithdrawalAppliedOnAllOffers"
        value={input.value}
      />
    )
  }, [])

  return (
    <div className="section vp-content-section bank-information">
      <div className="main-list-title title-actions-container">
        <h2 className="main-list-title-text">Modalités de retrait</h2>
      </div>

      <p className="bi-subtitle">
        Les modalités de retrait s’appliqueront par défaut à la création de vos
        offres. Vous pourrez modifier cette information à l’échelle de l’offre.
      </p>

      {!readOnly ? (
        <>
          {isCreatedEntity && <HiddenField name="withdrawalDetails" />}
          <Field
            name="withdrawalDetails"
            parse={value => value}
            render={renderWithdrawalDetails}
          />
          {!isCreatedEntity && (
            <Field
              name="isWithdrawalAppliedOnAllOffers"
              render={renderIsAppliedWithdrawalOnAllOffers}
              type="checkbox"
            />
          )}
        </>
      ) : (
        <span>{initialWithdrawalDetails}</span>
      )}
    </div>
  )
}

WithdrawalDetailsFields.defaultProps = {
  initialWithdrawalDetails: '',
  isCreatedEntity: false,
  readOnly: false,
}

WithdrawalDetailsFields.propTypes = {
  initialWithdrawalDetails: PropTypes.string,
  isCreatedEntity: PropTypes.bool,
  readOnly: PropTypes.bool,
}

export default WithdrawalDetailsFields
