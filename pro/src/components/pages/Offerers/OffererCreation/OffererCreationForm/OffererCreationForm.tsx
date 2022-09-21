import React, { useCallback } from 'react'
import type { FormRenderProps, FormSpyRenderProps } from 'react-final-form'
import { FormSpy } from 'react-final-form'
import { Link } from 'react-router-dom'

import { CreateOffererQueryModel } from 'apiClient/v1'
import { SirenField } from 'components/layout/form/fields/SirenField'

interface IOffererCreationForm
  extends Pick<FormRenderProps, 'handleSubmit' | 'invalid' | 'pristine'> {
  backTo: string
}

const OffererCreationForm = ({
  backTo,
  handleSubmit,
  invalid,
  pristine,
}: IOffererCreationForm): JSX.Element => {
  const renderAddress = useCallback(
    ({ values }: FormSpyRenderProps<CreateOffererQueryModel>) => (
      <div className="op-detail-creation-form">
        <span>{'Siège social : '}</span>
        {values.postalCode && (
          <span>
            {`${values.address} - ${values.postalCode} ${values.city}`}
          </span>
        )}
      </div>
    ),
    []
  )
  const renderName = useCallback(
    ({ values }: FormSpyRenderProps<CreateOffererQueryModel>) => (
      <div className="op-detail-creation-form">
        <span>{'Désignation : '}</span>
        {values.name && <span>{values.name}</span>}
      </div>
    ),
    []
  )

  return (
    <form onSubmit={handleSubmit}>
      <div className="section">
        <div className="op-creation-form">
          <SirenField />
          <FormSpy<CreateOffererQueryModel> render={renderName} />
          <FormSpy<CreateOffererQueryModel> render={renderAddress} />
        </div>
        <div className="offerer-form-validation">
          <div className="control">
            <Link className="secondary-link" to={backTo}>
              Retour
            </Link>
          </div>
          <div className="control">
            <button
              className="primary-button"
              disabled={invalid || pristine}
              type="submit"
            >
              Créer
            </button>
          </div>
        </div>
      </div>
    </form>
  )
}

export default OffererCreationForm
