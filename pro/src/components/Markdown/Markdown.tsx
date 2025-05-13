import DOMPurify from 'dompurify'

import styles from './Markdown.module.scss'

const BOLD_REGEXP = /\*\*(.*?)\*\*/gim
const ITALIC_REGEXP = /_(.*?)_/gim
const URL_REGEXP = /((https?:\/\/)|(www\.))[^\s/$.?#].[^\s]*/gim
const EMAIL_REGEXP =
  /(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))/gim

function markdownToHtml(markdown: string) {
  markdown = markdown.replace(BOLD_REGEXP, '<strong>$1</strong>')
  markdown = markdown.replace(ITALIC_REGEXP, '<em>$1</em>')
  markdown = markdown.replace(URL_REGEXP, (url) => {
    const href = url.match('^https?://') ? url : `https://${url}`
    return `<a class="${styles['markdown-link']}" href="${href}" rel="noreferrer" target="_blank">${url}</a>`
  })
  return markdown.replace(EMAIL_REGEXP, (email) => {
    return `<a href="mailto:${email}">${email}</a>`
  })
}

const cropText = (
  text: string,
  maxLength: number,
  croppedTextEnding: string = '...'
): string => {
  if (text.trim().length > maxLength) {
    return `${text.slice(0, maxLength)}${croppedTextEnding}`
  }
  return text
}

export const Markdown = ({
  markdownText,
  maxLength,
  croppedTextEnding,
}: {
  markdownText: string
  maxLength?: number
  croppedTextEnding?: string
}) => {
  const html = DOMPurify.sanitize(markdownToHtml(markdownText), {
    ALLOWED_TAGS: ['strong', 'em', 'a'],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'class'],
  })

  return (
    <span
      className={styles['markdown']}
      data-testid="markdown-content"
      dangerouslySetInnerHTML={{
        __html:
          maxLength === undefined
            ? html
            : cropText(html, maxLength, croppedTextEnding),
      }}
    />
  )
}
