import React from 'react'

import { ReactComponent as PenIcon } from 'icons/ico-pen.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import TooltipWrapper from 'ui-kit/TooltipWrapper'

import styles from '../../OfferItem.module.scss'

const DeleteDraftCell = () => {
  return (
    <td className={styles['draft-column']}>
      <TooltipWrapper title="Supprimer le brouillon" delay={0}>
        <ButtonLink
          variant={ButtonVariant.SECONDARY}
          link={{ isExternal: false, to: '/notImplemented' }}
          className={styles['button']}
        >
          <PenIcon
            title={`- supprimer le brouillon`}
            className={styles['button-icon']}
          />
        </ButtonLink>
      </TooltipWrapper>
    </td>
  )
}

export default DeleteDraftCell
