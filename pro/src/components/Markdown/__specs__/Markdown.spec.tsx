import { render } from '@testing-library/react'

import { Markdown } from '../Markdown'

function renderMarkdown(text: string) {
  return render(<Markdown markdownText={text} />)
}

describe('Markdown', () => {
  it('should render bold text with <strong> tag', () => {
    const component = renderMarkdown('**texte en gras**')
    expect(component.container.innerHTML).toContain(
      '<span><strong>texte en gras</strong></span>'
    )
  })

  it('should render italic text with <em> tag', () => {
    const component = renderMarkdown('_texte en italique_')
    expect(component.container.innerHTML).toContain(
      '<span><em>texte en italique</em></span>'
    )
  })

  it('should render urls with <a> tag', () => {
    const component = renderMarkdown('https://example.com')
    expect(component.container.innerHTML).toContain(
      '<span><a rel="noreferrer" href="https://example.com">https://example.com</a></span>'
    )
  })

  it('should render urls without http prefix with <a> tag', () => {
    const component = renderMarkdown('www.example.com')
    expect(component.container.innerHTML).toContain(
      '<span><a rel="noreferrer" href="https://www.example.com">www.example.com</a></span>'
    )
  })

  it('should render email adress with <a> tag and mailto attribute', () => {
    const component = renderMarkdown('test@example.com')
    expect(component.container.innerHTML).toContain(
      '<span><a href="mailto:test@example.com">test@example.com</a></span>'
    )
  })

  it('should render multiple strong tags when multiple words are surrounded with double asterisks', () => {
    const component = renderMarkdown('**texte** en **gras**')
    expect(component.container.innerHTML).toContain(
      '<span><strong>texte</strong> en <strong>gras</strong></span>'
    )
  })

  it('should render multiple em tags when multiple words are surrounded with underscores', () => {
    const component = renderMarkdown('_texte_ en _italique_')
    expect(component.container.innerHTML).toContain(
      '<span><em>texte</em> en <em>italique</em></span>'
    )
  })
})
