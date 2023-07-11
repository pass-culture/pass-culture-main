import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import { getError, isErrorAPIError } from 'apiClient/helpers'
import { PostVenueProviderBody, VenueProviderResponse } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Button } from 'ui-kit/index'

import { InitialValuesProps } from '../AllocineProviderForm/AllocineProviderForm'
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

  const editVenueProvider = useCallback(
    (payload: PostVenueProviderBody) => {
      api
        .updateVenueProvider(payload)
        .then(editedVenueProvider => {
          afterVenueProviderEdit(editedVenueProvider)
          notification.success(
            "Les modifications ont bien été importées et s'appliqueront aux nouvelles séances créées."
          )
        })
        .catch(error => {
          if (isErrorAPIError(error)) {
            notification.error(getRequestErrorStringFromErrors(getError(error)))
          }
        })
    },
    [afterVenueProviderEdit]
  )

  const openFormDialog = useCallback(() => {
    setIsOpenedFormDialog(true)
  }, [])

  const closeFormDialog = useCallback(() => {
    setIsOpenedFormDialog(false)
  }, [])

  const onConfirmDialog = useCallback(
    (payload: PostVenueProviderBody) => {
      payload = {
        ...payload,
        isActive: venueProvider.isActive,
      }
      editVenueProvider(payload)

      closeFormDialog()
    },
    [closeFormDialog, editVenueProvider]
  )

  // FIX ME: we should not use as but type of initialValues is strange
  const initialValues = {
    price: venueProvider.price,
    quantity: venueProvider.quantity,
    isDuo: venueProvider.isDuo ?? true,
  } as InitialValuesProps

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
