/**
 * Stores an input initial state and restores if modal gets dismissed.
 *
 * We have two behaviors:
 *
 * 1. checkbox: will store the `checked` as initial value
 * 1. other inputs: will store the `value` as initial value
 *
 * Add `data-confirm-modal=".my-modal-123"` on your input with `.my-modal-123` being a unique class on your `.modal`.
 *
 * @example
 * <input type="checkbox" value="on" data-confirm-modal=".my-modal" />
 * <div class="modal my-modal">
 *     <!-- modal content -->
 * </div>
 */
class PcConfirmModal extends PcAddOn {

    static CONFIRM_INPUT_SELECTOR = '[data-confirm-modal]'

    state = {}

    get $inputs() {
        return document.querySelectorAll(PcConfirmModal.CONFIRM_INPUT_SELECTOR)
    }

    initialize = () => {
        this.$inputs.forEach(($input) => {
            $input.dataset.initialValue = ['checkbox', 'radio'].includes($input.type) ? $input.checked : $input.value
        })
    }

    bindEvents = () => {
        EventHandler.on(document.body, 'change', PcConfirmModal.CONFIRM_INPUT_SELECTOR, this.#onChange)
    }

    unbindEvents = () => {
        EventHandler.off(document.body, 'change', PcConfirmModal.CONFIRM_INPUT_SELECTOR, this.#onChange)
    }

    #onChange = (event) => {
        const $input = event.target
        const { confirmModal } = $input.dataset
        const $modal = document.querySelector(confirmModal)
        this.state.$input = $input
        $modal.addEventListener('hidden.bs.modal', this.#restoreToInitialValue)
    }

    #restoreToInitialValue = () => {
        const { $input } = this.state
        if (['checkbox', 'radio'].includes($input.type)) {
            $input.checked = $input.dataset.initialValue === 'true'
        } else {
            $input.value = $input.dataset.initialValue
        }

        const $modal = document.querySelector($input.dataset.confirmModal)
        $modal.removeEventListener('hidden.bs.modal', this.#restoreToInitialValue)
        delete this.state.$input
    }
}
