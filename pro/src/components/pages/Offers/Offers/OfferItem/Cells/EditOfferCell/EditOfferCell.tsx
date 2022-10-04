import React from 'react'

import useAnalytics from 'components/hooks/useAnalytics'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { ReactComponent as PenIcon } from 'icons/ico-pen.svg'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from '../../OfferItem.module.scss'

const EditOfferCell = ({
  isOfferEditable,
  editionOfferLink,
  name,
}: {
  isOfferEditable: boolean
  editionOfferLink: string
  name: string
}) => {
  const { logEvent } = useAnalytics()
  return (
    <td className={styles['edit-column']}>
      {isOfferEditable && (
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          onClick={() =>
            logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
              from: OFFER_FORM_NAVIGATION_IN.OFFERS,
              to: OfferBreadcrumbStep.SUMMARY,
              used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_PEN,
              isEdition: true,
            })
          }
          link={{ isExternal: false, to: editionOfferLink }}
          className={styles['button']}
        >
          <PenIcon
            title={`${name} - éditer l'offre`}
            className={styles['button-icon']}
          />
        </ButtonLink>
      )}
    </td>
  )
}

export default EditOfferCell
