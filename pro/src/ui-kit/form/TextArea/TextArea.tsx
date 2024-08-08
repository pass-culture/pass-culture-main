import cn from 'classnames'
import {
  FieldHelperProps,
  FieldInputProps,
  FieldMetaProps,
  useField,
} from 'formik'
import Textarea from 'react-autosize-textarea'

import {
  FieldLayout,
  FieldLayoutBaseProps,
} from '../shared/FieldLayout/FieldLayout'

import styles from './TextArea.module.scss'

type TextAreaProps = React.InputHTMLAttributes<HTMLTextAreaElement> &
  FieldLayoutBaseProps & {
    rows?: number
    countCharacters?: boolean
    maxLength?: number
  }

export const TextArea = ({
  name,
  className,
  disabled,
  description,
  placeholder,
  label,
  maxLength = 1000,
  countCharacters,
  isOptional,
  smallLabel,
  rows = 7,
}: TextAreaProps): JSX.Element => {
  //  Temporary type fix while react-autosoze-textarea types are not in sync with the latest React types
  //  see https://github.com/DefinitelyTyped/DefinitelyTyped/pull/68984
  const [field, meta] = useField({ name }) as [
    FieldInputProps<string | undefined> & {
      onPointerEnterCapture: any
      onPointerLeaveCapture: any
    },
    FieldMetaProps<string>,
    FieldHelperProps<string>,
  ]

  return (
    <FieldLayout
      className={className}
      count={countCharacters ? field.value?.length : undefined}
      error={meta.error}
      isOptional={isOptional}
      label={label}
      maxLength={maxLength}
      name={name}
      showError={meta.touched && !!meta.error}
      smallLabel={smallLabel}
      description={description}
    >
      <Textarea
        aria-invalid={meta.touched && !!meta.error}
        {...(description ? { 'aria-describedby': `description-${name}` } : {})}
        className={cn(styles['text-area'], {
          [styles['has-error']]: meta.touched && !!meta.error,
        })}
        disabled={disabled}
        id={name}
        rows={rows}
        maxLength={maxLength}
        placeholder={placeholder}
        aria-required={!isOptional}
        {...field}
      />
    </FieldLayout>
  )
}
