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

export const Markdown = ({ markdownText }: { markdownText: string }) => {
  const html = DOMPurify.sanitize(markdownToHtml(markdownText), {
    ALLOWED_TAGS: ['strong', 'em', 'a'],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'class'],
  })
  return <span className={styles['markdown']} dangerouslySetInnerHTML={{ __html: html }} />
}
