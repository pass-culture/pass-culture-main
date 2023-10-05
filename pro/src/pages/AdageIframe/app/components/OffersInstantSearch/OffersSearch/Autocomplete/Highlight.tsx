import { parseAlgoliaHitHighlight } from '@algolia/autocomplete-preset-algolia'
import { createElement, Fragment } from 'react'

import { SuggestionItem } from './Autocomplete'

type HighlightHitParams = {
  hit: SuggestionItem
  attribute: keyof SuggestionItem | string[]
  tagName?: string
}

export function Highlight({
  hit,
  attribute,
  tagName = 'mark',
}: HighlightHitParams): JSX.Element {
  return createElement(
    Fragment,
    {},
    parseAlgoliaHitHighlight({
      hit,
      attribute,
    }).map(({ value, isHighlighted }, index) => {
      if (isHighlighted) {
        return createElement(tagName, { key: index }, value)
      }

      return value
    })
  )
}
