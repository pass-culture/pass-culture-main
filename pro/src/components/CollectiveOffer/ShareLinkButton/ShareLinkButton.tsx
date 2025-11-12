import { forwardRef } from 'react'

import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import connectStrokeIcon from '@/icons/stroke-connect.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import styles from './ShareLinkButton.module.scss'

export const ShareLinkButton = forwardRef<
  HTMLButtonElement,
  React.ComponentProps<typeof Button>
>((props, ref) => {
  return (
    <div className={styles['share-link-container']}>
      <Button
        ref={ref}
        className={styles['share-link']}
        icon={connectStrokeIcon}
        variant={ButtonVariant.TERNARY}
        {...props}
      >
        Partager l’offre
        <Tag label="Nouveau" variant={TagVariant.NEW} />
      </Button>
    </div>
  )
})
