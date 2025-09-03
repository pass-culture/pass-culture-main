import { useDebounce } from 'use-debounce'

import styles from './TextInputCharactersCount.module.scss'

export type TextInputCharactersCountProps = {
  current: number
  max: number
  describeById: string
}

export function TextInputCharactersCount({
  current,
  max,
  describeById,
}: TextInputCharactersCountProps) {
  //  The real counter would be announced by assistive technologies after each character typed.
  //  Therefore, we need a debounced counter that only changes when the user stops typing.
  const [debouncedCount] = useDebounce(current, 1000)

  return (
    <span className={styles['characters-count']}>
      {/** biome-ignore lint/a11y/useSemanticElements: What we want here is an aria-live region.*/}
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
