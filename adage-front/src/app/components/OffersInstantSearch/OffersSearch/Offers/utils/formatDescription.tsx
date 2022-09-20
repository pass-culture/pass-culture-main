import React from 'react'

type WordOrLinkItem = { type: 'word' | 'link' | 'mail'; value: string }

// Found here: http://emailregex.com/
const EMAIL_REGEXP = new RegExp(
  /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
)

const addLinkItemWithSpace = (value: string, list: WordOrLinkItem[]) => {
  list.push({ type: 'link', value })
  list.push({ type: 'word', value: ' ' })
}

const addWordItemWithSpace = (value: string, list: WordOrLinkItem[]) => {
  list.push({ type: 'word', value })
  list.push({ type: 'word', value: ' ' })
}

const addMailItemWithSpace = (value: string, list: WordOrLinkItem[]) => {
  list.push({ type: 'mail', value })
  list.push({ type: 'word', value: ' ' })
}

export const formatDescription = (
  description?: string | null
): React.ReactNode => {
  if (!description) return

  const descriptionWordsItems: WordOrLinkItem[] = []

  description.split('\n').forEach(descriptionBloc => {
    descriptionBloc.split(' ').map(wordOrLink => {
      if (
        ['www', 'http://', 'https://'].some(linkPrefix =>
          wordOrLink.startsWith(linkPrefix)
        )
      ) {
        // add link with following space
        return addLinkItemWithSpace(wordOrLink, descriptionWordsItems)
      }

      if (wordOrLink.match(EMAIL_REGEXP)) {
        // add mail with following space
        return addMailItemWithSpace(wordOrLink, descriptionWordsItems)
      }

      // add word with following space
      return addWordItemWithSpace(wordOrLink, descriptionWordsItems)
    })

    // re add line break
    descriptionWordsItems.push({ type: 'word', value: '\n' })
  })

  return descriptionWordsItems.map(({ type, value }) => {
    if (type === 'link') {
      // links beginning with www opens with adage base url --> we add https:// before to prevent that
      if (value.startsWith('www')) {
        return (
          <a
            href={`https://${value}`}
            key={value}
            rel="noreferrer"
            target="_blank"
          >
            {value}
          </a>
        )
      }

      return (
        <a href={value} key={value} rel="noreferrer" target="_blank">
          {value}
        </a>
      )
    }

    if (type === 'mail') {
      return (
        <a href={`mailto:${value}`} key={value}>
          {value}
        </a>
      )
    }

    return value
  })
}
