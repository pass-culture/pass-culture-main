/**
 * Enables or disables highlight selection depending on selected categories.
 */
class PcOfferCriterionForm extends PcAddOn {
  static CATEGORIES_SELECTOR = '.pc-highlight-js-module';
  static CATEGORY_TO_DISPLAY_HIGHLIGHT = 'Temps de valorisations thématiques'
  static HIGHLIGHT_SELECTOR = '.pc-field-highlight'


  #initialize = () => {
    document.querySelectorAll(PcOfferCriterionForm.CATEGORIES_SELECTOR).forEach(($categoriesSelect) => {
      this.#categoriesChange({target: $categoriesSelect})
    })
  }

  bindEvents = () => {
    EventHandler.on(document.body, 'change', PcOfferCriterionForm.CATEGORIES_SELECTOR, this.#categoriesChange)
    this.#initialize()
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'change', PcOfferCriterionForm.CATEGORIES_SELECTOR, this.#categoriesChange)
  }

  #categoriesChange = (event) => {
    const $categoriesSelect = event.target
    const $highlight = $categoriesSelect.closest("FORM").querySelector(PcOfferCriterionForm.HIGHLIGHT_SELECTOR)

    if (!$highlight || $categoriesSelect.tagName !== 'SELECT') {
      return
    }

    let highlightCategorySelected = false
    if ($categoriesSelect && $categoriesSelect.selectedOptions.length > 0) {
      for(let i = 0; i < $categoriesSelect.selectedOptions.length; i++){
        if($categoriesSelect.selectedOptions[i].text === PcOfferCriterionForm.CATEGORY_TO_DISPLAY_HIGHLIGHT)
          {
          highlightCategorySelected = true
          break
        }
      }
    }

    if (highlightCategorySelected) {
      $highlight.classList.remove('d-none')
    } else {
      let highlightSelectElement = $highlight.querySelector('select')
      highlightSelectElement.remove(highlightSelectElement.selectedIndex)
      $highlight.classList.add('d-none')
    }
  }
}
