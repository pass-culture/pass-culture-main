import React, { useCallback } from 'react'
import type { FormRenderProps, FormSpyRenderProps } from 'react-final-form'
import { FormSpy } from 'react-final-form'

import { CreateOffererQueryModel } from 'apiClient/v1'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SirenField } from 'ui-kit/form_rff/fields/SirenField'

import styles from './OffererCreationForm.module.scss'

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
      <div className={styles['op-detail-creation-form']}>
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
      <div className={styles['op-detail-creation-form']}>
        <span>{'Désignation : '}</span>
        {values.name && <span>{values.name}</span>}
      </div>
    ),
    []
  )

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <div className={styles['op-creation-form']}>
          <SirenField />
          <FormSpy<CreateOffererQueryModel> render={renderName} />
          <FormSpy<CreateOffererQueryModel> render={renderAddress} />
        </div>
        <div className={styles['offerer-form-validation']}>
          <div>
            <ButtonLink
              variant={ButtonVariant.SECONDARY}
              link={{
                to: backTo,
                isExternal: false,
              }}
            >
              Retour
            </ButtonLink>
          </div>
          <div>
            <Button
              variant={ButtonVariant.PRIMARY}
              disabled={invalid || pristine}
              type="submit"
            >
              Créer
            </Button>
          </div>
        </div>
      </div>
    </form>
  )
}

export default OffererCreationForm
