import { render } from '@testing-library/react'

import { Markdown } from '../Markdown'

function renderMarkdown(text: string) {
  return render(<Markdown markdownText={text} />)
}

describe('Markdown', () => {
  it('should render bold text with <strong> tag', () => {
    const component = renderMarkdown('**texte en gras**')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown"><strong>texte en gras</strong></span>'
    )
  })

  it('should render italic text with <em> tag', () => {
    const component = renderMarkdown('_texte en italique_')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown"><em>texte en italique</em></span>'
    )
  })

  it('should render urls with <a> tag', () => {
    const component = renderMarkdown('https://example.com')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown"><a target="_blank" rel="noreferrer" href="https://example.com" class="markdown-link">https://example.com</a></span>'
    )
  })

  it('should render urls without http prefix with <a> tag', () => {
    const component = renderMarkdown('www.example.com')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown"><a target="_blank" rel="noreferrer" href="https://www.example.com" class="markdown-link">www.example.com</a></span>'
    )
  })

  it('should render email adress with <a> tag and mailto attribute', () => {
    const component = renderMarkdown('test@example.com')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown"><a href="mailto:test@example.com">test@example.com</a></span>'
    )
  })

  it('should render multiple strong tags when multiple words are surrounded with double asterisks', () => {
    const component = renderMarkdown('**texte** en **gras**')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown"><strong>texte</strong> en <strong>gras</strong></span>'
    )
  })

  it('should render multiple em tags when multiple words are surrounded with underscores', () => {
    const component = renderMarkdown('_texte_ en _italique_')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown"><em>texte</em> en <em>italique</em></span>'
    )
  })
})
