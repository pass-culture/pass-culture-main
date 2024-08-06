import cn from 'classnames'

import { Mode } from 'core/OfferEducational/types'
import fullValidateIcon from 'icons/full-validate.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

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
  return children ? (
    <div
      className={cn(style['right'], {
        [style['right-inverse']]: inverseWhenSmallerThanTablet,
      })}
    >
      {dirtyForm !== undefined && mode === Mode.CREATION ? (
        !dirtyForm ? (
          <span className={style['draft-indicator']}>
            <SvgIcon
              src={fullValidateIcon}
              alt=""
              width="16"
              className={style['draft-saved-icon']}
            />
            Brouillon enregistré
          </span>
        ) : (
          <span className={style['draft-indicator']}>
            <div className={style['draft-not-saved-icon']} />
            Brouillon non enregistré
          </span>
        )
      ) : null}
      {children}
    </div>
  ) : null
}
