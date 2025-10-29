/**
 * Displays the number of characters in a textarea.
 * @example
 * <textarea class="pc-textarea-counter"></textarea>
 * <span class="pc-textarea-counter-container">0</span>
 */ 
class PcTextareaCounter extends PcAddOn {
    static SELECTOR = '.pc-textarea-counter'
  
    bindEvents = () => {
      EventHandler.on(document.body, 'input', PcTextareaCounter.SELECTOR, this.#updateCounter)
    }

    unbindEvents = () => {
      EventHandler.off(document.body, 'input', PcTextareaCounter.SELECTOR, this.#updateCounter)
    }

    #updateCounter = (event) => {
      const $textarea = event.target
      const $container = $textarea.parentElement
      const $counter = $container.querySelector('.pc-textarea-counter-container')
      
      $counter.textContent = $textarea.value.length
    }
  }