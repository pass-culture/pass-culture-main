import React from 'react'

type WordOrLinkItem = { type: 'word' | 'link'; value: string }

const addLinkItemWithSpace = (value: string, list: WordOrLinkItem[]) => {
  list.push({ type: 'link', value })
  list.push({ type: 'word', value: ' ' })
}

const addWordItemWithSpace = (value: string, list: WordOrLinkItem[]) => {
  list.push({ type: 'word', value })
  list.push({ type: 'word', value: ' ' })
}

export const formatDescription = (description: string): React.ReactNode => {
  const descriptionWordsItems: WordOrLinkItem[] = []

  description.split('\n').forEach(descriptionBloc => {
    descriptionBloc.split(' ').map(wordOrLink => {
      if (
        ['www', 'http://', 'https://'].some(linkPrefix =>
          wordOrLink.startsWith(linkPrefix)
        )
      ) {
        // add link with following space
        addLinkItemWithSpace(wordOrLink, descriptionWordsItems)
      } else {
        // add word with following space
        addWordItemWithSpace(wordOrLink, descriptionWordsItems)
      }
    })

    // re add line break
    descriptionWordsItems.push({ type: 'word', value: '\n' })
  })

  return descriptionWordsItems.map(({ type, value }) => {
    if (type === 'link') {
      // links beginning with www opens with adage base url --> we add https:// before to prevent that
      if (value.startsWith('www')) {
        return (
          <a href={`https://${value}`} rel="noreferrer" target="_blank">
            {value}
          </a>
        )
      }

      return (
        <a href={value} rel="noreferrer" target="_blank">
          {value}
        </a>
      )
    }

    return value
  })
}
