import { useDebounce } from 'use-debounce'

import styles from './FieldLayoutCharacterCount.module.scss'

export type FieldLayoutCharacterCountProps = {
  count: number
  maxLength: number
  name: string
}

export function FieldLayoutCharacterCount({
  count,
  maxLength,
  name,
}: FieldLayoutCharacterCountProps) {
  //  The real counter would be announced by assistive technologies after each character typed.
  //  Therefore, we need a debounced counter that only changes when the user stops typing.
  const [debouncedCount] = useDebounce(count, 1000)

  return (
    <>
      {/** biome-ignore lint/a11y/useSemanticElements: We want a `role="status"` here, not an `<output />`. */}
      <span
        role="status"
        className={styles['visually-hidden']}
        id={`field-characters-count-${name}`}
      >
        {debouncedCount} caractères sur {maxLength}
      </span>
      <span
        className={styles['field-layout-character-count']}
        data-testid={`counter-${name}`}
        aria-hidden
      >
        {count}/{maxLength}
      </span>
    </>
  )
}
