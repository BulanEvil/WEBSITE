(function () {
  const script = document.currentScript;
  const assetBase = new URL("../contact/", script ? script.src : window.location.href);
  const contacts = {
    whatsapp: {
      title: "Annie",
      image: new URL("annie-whatsapp-cropped.jpg", assetBase).href,
      alt: "Annie WhatsApp QR code"
    },
    wechat: {
      title: "Annie",
      image: new URL("annie-wechat-cropped.jpg", assetBase).href,
      alt: "Annie WeChat QR code"
    }
  };

  let modal;
  let activeTrigger;

  function buildModal() {
    const node = document.createElement("div");
    node.className = "qr-modal";
    node.setAttribute("aria-hidden", "true");
    node.innerHTML = `
      <div class="qr-modal-panel" role="dialog" aria-labelledby="qr-modal-title">
        <button class="qr-modal-close" type="button" aria-label="Close QR code" data-qr-close>x</button>
        <div class="qr-modal-copy">
          <h2 id="qr-modal-title"></h2>
        </div>
        <div class="qr-modal-image-wrap">
          <img alt="" />
        </div>
      </div>
    `;
    document.body.appendChild(node);
    node.addEventListener("click", (event) => {
      if (event.target.closest("[data-qr-close]")) closeModal();
    });
    return node;
  }

  function positionModal(trigger) {
    if (!modal || !trigger) return;
    const panel = modal.querySelector(".qr-modal-panel");
    const rect = trigger.getBoundingClientRect();
    const gap = 12;
    const margin = 16;
    const panelWidth = panel.offsetWidth || 300;
    const left = Math.min(
      Math.max(rect.right - panelWidth, margin),
      window.innerWidth - panelWidth - margin
    );
    const top = Math.min(rect.bottom + gap, window.innerHeight - margin);
    modal.style.setProperty("--qr-left", `${left}px`);
    modal.style.setProperty("--qr-top", `${top}px`);
  }

  function openModal(type, trigger) {
    const contact = contacts[type];
    if (!contact) return;
    modal = modal || buildModal();
    activeTrigger = trigger;

    modal.querySelector("#qr-modal-title").textContent = contact.title;
    const image = modal.querySelector(".qr-modal-image-wrap img");
    image.src = contact.image;
    image.alt = contact.alt;

    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    positionModal(trigger);
  }

  function closeModal() {
    if (!modal || !modal.classList.contains("is-open")) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    activeTrigger = null;
  }

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest(".header-icon-button.whatsapp, .header-icon-button.wechat");
    if (!trigger) return;
    event.preventDefault();
    if (modal && modal.classList.contains("is-open") && activeTrigger === trigger) {
      closeModal();
      return;
    }
    openModal(trigger.classList.contains("wechat") ? "wechat" : "whatsapp", trigger);
  });

  document.addEventListener("click", (event) => {
    if (!modal || !modal.classList.contains("is-open")) return;
    if (event.target.closest(".qr-modal-panel")) return;
    if (event.target.closest(".header-icon-button.whatsapp, .header-icon-button.wechat")) return;
    closeModal();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeModal();
  });

  window.addEventListener("resize", () => positionModal(activeTrigger));
  window.addEventListener("scroll", () => positionModal(activeTrigger), true);
})();
