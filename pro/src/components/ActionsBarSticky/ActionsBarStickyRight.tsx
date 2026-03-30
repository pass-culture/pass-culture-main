import cn from 'classnames'

import { Mode } from '@/commons/core/OfferEducational/types'
import fullValidateIcon from '@/icons/full-validate.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import style from './ActionsBarSticky.module.scss'

interface ActionsBarStickyRightProps {
  children: React.ReactNode
  inverseWhenSmallerThanTablet?: boolean
  dirtyForm?: boolean
  mode?: Mode
}

export const Right = ({
  children,
  inverseWhenSmallerThanTablet = false,
  dirtyForm,
  mode,
}: ActionsBarStickyRightProps): JSX.Element | null => {
  const draftIndicator = dirtyForm ? (
    <span className={style['draft-indicator']}>
      <div className={style['draft-not-saved-icon']} />
      Brouillon non enregistré
    </span>
  ) : (
    <span className={style['draft-indicator']}>
      <SvgIcon
        src={fullValidateIcon}
        alt=""
        width="16"
        className={style['draft-saved-icon']}
      />
      Brouillon enregistré
    </span>
  )

  return children ? (
    <div
      className={cn(style['right'], {
        [style['right-inverse']]: inverseWhenSmallerThanTablet,
      })}
    >
      <output>
        {dirtyForm !== undefined && mode === Mode.CREATION
          ? draftIndicator
          : null}
      </output>
      {children}
    </div>
  ) : null
}
