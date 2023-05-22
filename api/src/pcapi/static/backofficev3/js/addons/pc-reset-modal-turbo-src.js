/**
 * Allows modal that contains turbo frame to reinitialize its src attribute when opening.
 *
 * This can be useful to reset a turbo frame when it changes its content using multiple endpoints,
 * as turbo frame will update its src attribute.
 *
 * @example
 * {% set turbo_src = url_for("backoffice_v3_web.users.get_batch_suspend_users_form") %}
 * <button class="btn btn-outline-primary lead fw-bold mt-2"
 *             data-reset-modal-url="{{ turbo_src }}"
 *             data-bs-toggle="modal"
 *             data-bs-target="#batch-suspend-users-form"
 *             type="button">Suspendre des utilisateurs en masse via leur ID</button>
 * {{ build_lazy_modal(turbo_src, "batch-suspend-users-form") }}
 */
class PcResetModalTurboSrc extends PcAddOn {
    static PC_RESET_MODAL_TURBO_SRC_SELECTOR = '[data-reset-modal-url]'

    bindEvents = () => {
        EventHandler.on(document.body, 'click', PcResetModalTurboSrc.PC_RESET_MODAL_TURBO_SRC_SELECTOR, this.#resetTurboFrameSrc)
    }

    unbindEvents = () => {
        EventHandler.on(document.body, 'click', PcResetModalTurboSrc.PC_RESET_MODAL_TURBO_SRC_SELECTOR, this.#resetTurboFrameSrc)
    }

    #resetTurboFrameSrc = (event) => {
        const { bsToggle, bsTarget, resetModalUrl } = event.target.dataset
        if (bsToggle === 'modal') {
            document.querySelector(bsTarget).querySelector('turbo-frame').src = resetModalUrl
        }
    }
}