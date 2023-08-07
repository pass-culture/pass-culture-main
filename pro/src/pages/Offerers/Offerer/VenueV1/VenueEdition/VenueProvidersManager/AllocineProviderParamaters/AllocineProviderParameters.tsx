import React, { useState } from 'react'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import { PostVenueProviderBody, VenueProviderResponse } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Button } from 'ui-kit/index'

import { FormValuesProps } from '../AllocineProviderForm/AllocineProviderForm'
import AllocineProviderFormDialog from '../AllocineProviderFormDialog/AllocineProviderFormDialog'
import { getRequestErrorStringFromErrors } from '../utils/getRequestErrorStringFromErrors'

import style from './AllocineProviderParameters.module.scss'

interface AllocineProviderParametersProps {
  venueProvider: VenueProviderResponse
  afterVenueProviderEdit: (editedVenueProvider: VenueProviderResponse) => void
  offererId: number
}

const AllocineProviderParameters = ({
  venueProvider,
  afterVenueProviderEdit,
  offererId,
}: AllocineProviderParametersProps): JSX.Element => {
  const [isOpenedFormDialog, setIsOpenedFormDialog] = useState(false)
  const notification = useNotification()

  const editVenueProvider = (payload: PostVenueProviderBody): boolean => {
    let isSucess = false

    api
      .updateVenueProvider(payload)
      .then(editedVenueProvider => {
        afterVenueProviderEdit(editedVenueProvider)
        notification.success(
          "Les modifications ont bien été importées et s'appliqueront aux nouvelles séances créées."
        )
        isSucess = true
      })
      .catch(error => {
        isSucess = false
        if (isErrorAPIError(error)) {
          notification.error(getRequestErrorStringFromErrors(getError(error)))
        }
      })

    return isSucess
  }

  const openFormDialog = () => {
    setIsOpenedFormDialog(true)
  }

  const closeFormDialog = () => {
    setIsOpenedFormDialog(false)
  }

  const onConfirmDialog = (payload: PostVenueProviderBody): boolean => {
    payload = {
      ...payload,
      isActive: venueProvider.isActive,
    }
    const isSuccess = editVenueProvider(payload)

    closeFormDialog()
    return isSuccess
  }

  const initialValues: FormValuesProps = {
    price: venueProvider.price ? venueProvider.price : '',
    quantity: venueProvider.quantity ? Number(venueProvider.quantity) : '',
    isDuo: venueProvider.isDuo ?? false,
  }

  return (
    <div className={style['allocine-provider-parameters-container']}>
      <h4 className={style['title']}>Paramètres des offres synchronisées</h4>
      <div className={style['parameters-list']}>
        <div className={style['parameter-item']}>
          Prix de vente/place :{' '}
          <span>
            {venueProvider.price
              ? `${new Intl.NumberFormat('fr-FR', {
                  style: 'currency',
                  currency: 'EUR',
                }).format(venueProvider.price)}`
              : ''}
          </span>
        </div>
        <div className={style['parameter-item']}>
          Nombre de places/séance :{' '}
          <span>
            {`${
              typeof venueProvider.quantity === 'number'
                ? venueProvider.quantity
                : 'Illimité'
            }`}
          </span>
        </div>
        <div className={style['parameter-item']}>
          Accepter les offres DUO :{' '}
          <span>{`${venueProvider.isDuo ? 'Oui' : 'Non'} `}</span>
        </div>
      </div>
      <Button
        className={style['edit-parameters-btn']}
        variant={ButtonVariant.SECONDARY}
        onClick={openFormDialog}
      >
        Modifier les paramètres
      </Button>
      {isOpenedFormDialog && (
        <AllocineProviderFormDialog
          initialValues={initialValues}
          onCancel={closeFormDialog}
          onConfirm={onConfirmDialog}
          providerId={venueProvider.provider.id}
          venueId={venueProvider.venueId}
          offererId={offererId}
        />
      )}
    </div>
  )
}

export default AllocineProviderParameters
