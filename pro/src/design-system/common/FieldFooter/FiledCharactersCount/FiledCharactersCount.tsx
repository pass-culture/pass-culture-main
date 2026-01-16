import { useDebounce } from 'use-debounce'

import styles from './FiledCharactersCount.module.scss'

type FiledCharactersCountProps = {
  current: number
  max: number
  describeById: string
}

export function FiledCharactersCount({
  current,
  max,
  describeById,
}: FiledCharactersCountProps) {
  //  The real counter would be announced by assistive technologies after each character typed.
  //  Therefore, we need a debounced counter that only changes when the user stops typing.
  const [debouncedCount] = useDebounce(current, 1000)

  return (
    <span className={styles['characters-count']}>
      {/** biome-ignore lint/a11y/useSemanticElements: We want a `role="status"` here, not an `<output />`. */}
      <span
        role="status"
        className={styles['visually-hidden']}
        id={describeById}
      >
        {debouncedCount} caractères sur {max}
      </span>
      <span
        className={styles['field-layout-character-count']}
        aria-hidden="true"
      >
        {current}/{max}
      </span>
    </span>
  )
}
