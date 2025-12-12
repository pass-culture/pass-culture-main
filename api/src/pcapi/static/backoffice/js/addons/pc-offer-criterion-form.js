/**
 * Enables or disables highlight selection depending on selected categories.
 */
class PcOfferCriterionForm extends PcAddOn {
  static CATEGORIES_SELECTOR = 'form[name="tags_create"] .pc-field-categories select, form[name^="tags_"][name$="_update"] .pc-field-categories select';
  static HIGHLIGHT_SELECTOR = '.pc-field-highlight'


  initialize = () => {
    const $categoriesSelect = document.querySelector(PcOfferCriterionForm.CATEGORIES_SELECTOR)
    if ($categoriesSelect) {
      this._categoriesChange({target: $categoriesSelect})
    }
  }

  bindEvents = () => {
    EventHandler.on(document.body, 'change', PcOfferCriterionForm.CATEGORIES_SELECTOR, this._categoriesChange)

    const callback = (mutationsList, observer) => {
      for (const mutation of mutationsList) {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach(node => {
            if (node.nodeType !== 1) return;  // nodeType === 1 if HTML element
            const $categoriesSelect = node.matches(PcOfferCriterionForm.CATEGORIES_SELECTOR) ? node : node.querySelector(PcOfferCriterionForm.CATEGORIES_SELECTOR);
            if ($categoriesSelect) {
              this._categoriesChange({target: $categoriesSelect})
              return;
            }
          });
        }
      }
    };

  const observer = new MutationObserver(callback);
  observer.observe(document.body, { childList: true, subtree: true });
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'change', PcOfferCriterionForm.CATEGORIES_SELECTOR, this._categoriesChange)
    if (this._observer) this._observer.disconnect()
  }

  _categoriesChange = (event) => {
    const $categoriesSelect = event.target
    const $highlight = document.querySelector(PcOfferCriterionForm.HIGHLIGHT_SELECTOR)
    let highlightCategorySelected = undefined
    if ($categoriesSelect && $categoriesSelect.selectedOptions.length > 0) {
      highlightCategorySelected = Array.from($categoriesSelect.selectedOptions).some(option => option.text === 'Temps de valorisations thématiques')
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
