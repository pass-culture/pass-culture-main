import cn from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './RadioButton.module.scss'

/**
 * Props communes à tous les RadioButton
 * @property label - Label affiché à côté du bouton (obligatoire)
 * @property name - Nom du groupe radio (obligatoire)
 * @property value - Valeur du bouton (obligatoire)
 * @property className - Classe CSS additionnelle
 * @property checked - Si le bouton est sélectionné
 * @property ariaDescribedBy - id(s) pour aria-describedby
 * @property variant - Variante d'affichage ('DEFAULT' ou 'DETAILED')
 * @property sizing - Taille du composant ('HUG' ou 'FILL')
 */
type CommonProps = Partial<React.InputHTMLAttributes<HTMLInputElement>> & {
  /** Label affiché à côté du bouton */
  label: string
  /** Nom du groupe radio */
  name: string
  /** Valeur du bouton */
  value: string
  /** Classe CSS additionnelle */
  className?: string
  /** Si le bouton est sélectionné */
  checked?: boolean
  /** id(s) pour aria-describedby */
  ariaDescribedBy?: string
  /** Variante d'affichage */
  variant?: 'DEFAULT' | 'DETAILED'
  /** Taille du composant */
  sizing?: 'HUG' | 'FILL'
}

// ---------------
// Variant DEFAULT
// ---------------

/**
 * Props pour la variante DEFAULT
 * @property description - Jamais utilisé ici
 * @property collapsed - Jamais utilisé ici
 * @property icon - Jamais utilisé ici
 * @property tag - Jamais utilisé ici
 * @property text - Jamais utilisé ici
 * @property image - Jamais utilisé ici
 * @property imageSize - Jamais utilisé ici
 */
type DefaultVariantProps = CommonProps & {
  variant?: 'DEFAULT'
  sizing?: 'HUG'
  description?: never
  collapsed?: never
  icon?: never
  tag?: never
  text?: never
  image?: never
  imageSize?: never
}

// ---------------
// Variant DETAILED
// ---------------

/**
 * Props pour la variante DETAILED
 * @property description - Description optionnelle (uniquement pour la variante DETAILED)
 * @property collapsed - Élément JSX affiché si coché
 */
type DetailedWithDescriptionProps = {
  /** Description optionnelle (uniquement pour la variante DETAILED) */
  description?: string
  /** Élément JSX affiché si coché */
  collapsed?: JSX.Element
}

// Right element is an "icon" string
/**
 * Variante DETAILED avec icône à droite
 * @property icon - Nom de l'icône
 */
type DetailedWithIconProps = DetailedWithDescriptionProps & {
  /** Nom de l'icône */
  icon: string
  tag?: never
  text?: never
  image?: never
  imageSize?: never
}

// Right element is tag Element
/**
 * Variante DETAILED avec tag à droite
 * @property tag - Élément JSX
 */
type DetailedWithTagProps = DetailedWithDescriptionProps & {
  icon?: never
  /** Élément JSX */
  tag: JSX.Element
  text?: never
  image?: never
  imageSize?: never
}

// Right element is simple "text" string
/**
 * Variante DETAILED avec texte à droite
 * @property text - Texte à afficher
 */
type DetailedWithTextProps = DetailedWithDescriptionProps & {
  icon?: never
  tag?: never
  /** Texte à afficher */
  text: string
  image?: never
  imageSize?: never
}

// Right element is an "image", and can eventually have a size
/**
 * Variante DETAILED avec image à droite
 * @property image - URL de l'image
 * @property imageSize - Taille de l'image ('S', 'M', 'L')
 */
type DetailedWithImageProps = DetailedWithDescriptionProps & {
  icon?: never
  tag?: never
  text?: never
  /** URL de l'image */
  image: string
  /** Taille de l'image */
  imageSize?: 'S' | 'M' | 'L'
}

/**
 * Variante DETAILED sans élément à droite
 */
type DetailedWithNothingProps = DetailedWithDescriptionProps & {
  icon?: never
  tag?: never
  text?: never
  image?: never
  imageSize?: never
}

// Specific to DETAILED variant
/**
 * Props spécifiques à la variante DETAILED
 * @property variant - Doit être 'DETAILED'
 */
type DetailedVariantProps = CommonProps & {
  variant: 'DETAILED'
} & (
    | DetailedWithIconProps
    | DetailedWithTagProps
    | DetailedWithTextProps
    | DetailedWithImageProps
    | DetailedWithNothingProps
  )

// Final assembled type for RadioButton Component
/**
 * Props du composant RadioButton (DEFAULT ou DETAILED)
 */
type RadioButtonProps = DefaultVariantProps | DetailedVariantProps

export const RadioButton = forwardRef(
  (
    {
      label,
      value,
      variant = 'DEFAULT',
      sizing,
      className,
      description,
      collapsed,
      icon,
      tag,
      text,
      image,
      imageSize = 'S',
      ...props
    }: RadioButtonProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const id = useId()

    const isVariantDetailed = variant === 'DETAILED'

    return (
      <>
        <div
          className={cn(
            styles['radio-button'],
            {
              [styles['sizing-fill']]: sizing === 'FILL',
              [styles['variant-detailed']]: isVariantDetailed,
              [styles['has-children']]: collapsed,
              [styles['is-checked']]: props.checked,
              [styles['is-disabled']]: props.disabled,
            },
            className
          )}
        >
          <label htmlFor={id} className={styles['radio-button-label']}>
            <input
              type="radio"
              {...props}
              value={value}
              className={styles[`radio-button-input`]}
              id={id}
              ref={ref}
              {...(props.checked !== undefined
                ? { checked: props.checked }
                : {})} // To handle uncontrolled component
            />
            <div>
              {label}
              {description && isVariantDetailed && (
                <p className={styles['description']}>{description}</p>
              )}
            </div>
            {tag && isVariantDetailed && (
              <div className={styles['right-tag']}>{tag}</div>
            )}
            {icon && isVariantDetailed && (
              <div className={styles['right-icon']}>
                <SvgIcon
                  src={icon}
                  alt=""
                  className={styles['right-icon-svg']}
                />
              </div>
            )}
            {text && isVariantDetailed && (
              <div className={styles['right-text']}>{text}</div>
            )}
            {image && isVariantDetailed && (
              <div className={styles['right-image']}>
                <img
                  src={image}
                  alt=""
                  className={cn({
                    [styles['right-image-img-small']]: imageSize === 'S',
                    [styles['right-image-img-medium']]: imageSize === 'M',
                    [styles['right-image-img-large']]: imageSize === 'L',
                  })}
                />
              </div>
            )}
          </label>
          {collapsed && isVariantDetailed && props.checked && (
            <div className={styles['children-on-checked']}>{collapsed}</div>
          )}
        </div>
      </>
    )
  }
)
RadioButton.displayName = 'RadioButton'
