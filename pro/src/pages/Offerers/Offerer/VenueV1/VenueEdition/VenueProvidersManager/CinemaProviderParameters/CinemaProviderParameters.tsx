import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import { VenueProviderResponse } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Button } from 'ui-kit/index'

import { CinemaProviderFormDialog } from '../CinemaProviderFormDialog/CinemaProviderFormDialog'

import style from './CinemaProviderParameters.module.scss'
import { ICinemaProviderParametersValues } from './types'

export interface ICinemaProviderParametersProps {
  venueProvider: VenueProviderResponse
  afterVenueProviderEdit: (editedVenueProvider: VenueProviderResponse) => void
}

const CinemaProviderParameters = ({
  venueProvider,
  afterVenueProviderEdit,
}: ICinemaProviderParametersProps): JSX.Element => {
  const [isOpenedFormDialog, setIsOpenedFormDialog] = useState(false)
  const notification = useNotification()

  const editVenueProvider = useCallback(
    (payload: ICinemaProviderParametersValues) => {
      api
        .updateVenueProvider(payload)
        .then(editedVenueProvider => {
          afterVenueProviderEdit(editedVenueProvider)
          notification.success(
            "Les modifications ont bien été importées et s'appliqueront aux nouvelles séances créées."
          )
        })
        .catch(() => {
          notification.error("Une erreur s'est produite, veuillez réessayer")
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
    (payload: ICinemaProviderParametersValues) => {
      payload = {
        ...payload,
        isActive: venueProvider.isActive,
      }
      editVenueProvider(payload)

      closeFormDialog()
    },
    [closeFormDialog, editVenueProvider]
  )

  const initialValues = {
    isDuo: venueProvider.isDuo,
  }

  return (
    <div className={style['cinema-provider-parameters']}>
      <h4 className={style['title']}>Paramètres des offres synchronisées</h4>
      <div className={style['cinema-provider-parameters-list']}>
        <div>
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
        <CinemaProviderFormDialog
          initialValues={initialValues}
          onCancel={closeFormDialog}
          onConfirm={onConfirmDialog}
          providerId={venueProvider.providerId}
          venueId={venueProvider.venueId}
        />
      )}
    </div>
  )
}

export default CinemaProviderParameters
