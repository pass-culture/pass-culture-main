import { render } from '@testing-library/react'

import { Markdown } from '../Markdown'

function renderMarkdown(
  text: string,
  maxLength?: number,
  croppedTextEnding?: string
) {
  return render(
    <Markdown
      markdownText={text}
      maxLength={maxLength}
      croppedTextEnding={croppedTextEnding}
    />
  )
}

describe('Markdown', () => {
  it('should render bold text with <strong> tag', () => {
    const component = renderMarkdown('**texte en gras**')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown" data-testid="markdown-content"><strong>texte en gras</strong></span>'
    )
  })

  it('should render italic text with <em> tag', () => {
    const component = renderMarkdown('_texte en italique_')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown" data-testid="markdown-content"><em>texte en italique</em></span>'
    )
  })

  it('should render urls with <a> tag', () => {
    const component = renderMarkdown('https://example.com')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown" data-testid="markdown-content"><a target="_blank" rel="noreferrer" href="https://example.com" class="markdown-link">https://example.com</a></span>'
    )
  })

  it('should render urls without http prefix with <a> tag', () => {
    const component = renderMarkdown('www.example.com')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown" data-testid="markdown-content"><a target="_blank" rel="noreferrer" href="https://www.example.com" class="markdown-link">www.example.com</a></span>'
    )
  })

  it('should render email adress with <a> tag and mailto attribute', () => {
    const component = renderMarkdown('test@example.com')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown" data-testid="markdown-content"><a href="mailto:test@example.com">test@example.com</a></span>'
    )
  })

  it('should render multiple strong tags when multiple words are surrounded with double asterisks', () => {
    const component = renderMarkdown('**texte** en **gras**')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown" data-testid="markdown-content"><strong>texte</strong> en <strong>gras</strong></span>'
    )
  })

  it('should render multiple em tags when multiple words are surrounded with underscores', () => {
    const component = renderMarkdown('_texte_ en _italique_')
    expect(component.container.innerHTML).toContain(
      '<span class="markdown" data-testid="markdown-content"><em>texte</em> en <em>italique</em></span>'
    )
  })

  it('should crop text', () => {
    const component = renderMarkdown(
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur',
      50
    )
    expect(component.container.innerHTML).toContain(
      '<span class="markdown" data-testid="markdown-content">Lorem ipsum dolor sit amet, consectetur adipiscing...</span>'
    )
    const componentWithCustomCroppedEnding = renderMarkdown(
      'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur',
      50,
      ' Afficher plus...'
    )
    expect(componentWithCustomCroppedEnding.container.innerHTML).toContain(
      '<span class="markdown" data-testid="markdown-content">Lorem ipsum dolor sit amet, consectetur adipiscing Afficher plus...</span>'
    )
  })
})
