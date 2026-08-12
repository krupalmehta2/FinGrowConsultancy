/* =====================================================================
   FINGROW CONSULTANCY SERVICES — MASTER JAVASCRIPT
   Vanilla JS only. No inline scripts anywhere in the templates.
   ===================================================================== */

(function () {
    "use strict";

    /* ---------------------------------------------------------------
       0. UTILITIES
    ---------------------------------------------------------------- */
    const $ = (selector, scope = document) => scope.querySelector(selector);
    const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));

    document.addEventListener("DOMContentLoaded", () => {
        initPageLoader();
        initStickyNavbar();
        initScrollProgress();
        initMobileMenu();
        initMobileAccordion();
        initBackToTop();
        initSmoothAnchorScroll();
        initNewsletterForm();
        initDjangoMessages();
        initCookieConsent();
        initFormFeedback();
    });

    /* ---------------------------------------------------------------
       1. PAGE LOADER
       Hides the branded loader once the window has fully loaded.
    ---------------------------------------------------------------- */
    function initPageLoader() {
        const loader = $("#fgLoader");
        if (!loader) return;

        window.addEventListener("load", () => {
            loader.classList.add("fg-loader--hidden");
            window.setTimeout(() => loader.remove(), 600);
        });
    }

    /* ---------------------------------------------------------------
       2. AOS — ANIMATE ON SCROLL INIT
    ---------------------------------------------------------------- */
    function initAOS() {
        if (typeof AOS === "undefined") return;
        AOS.init({
            duration: 700,
            easing: "ease-out-cubic",
            once: true,
            offset: 60
        });
    }

    /* ---------------------------------------------------------------
       3. STICKY NAVBAR
       Transparent over the hero, solid + shadow once user scrolls.
    ---------------------------------------------------------------- */
    function initStickyNavbar() {
        const header = $("#fgHeader");
        if (!header) return;
        // The header is intentionally always solid: this keeps navigation
        // readable and avoids scroll-driven layout/color changes.
        header.classList.add("fg-header--solid");
    }

    /* ---------------------------------------------------------------
       4. SCROLL PROGRESS BAR
    ---------------------------------------------------------------- */
    function initScrollProgress() {
        const bar = $("#fgScrollProgressBar");
        if (!bar) return;

        const updateProgress = () => {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
            bar.style.width = progress + "%";
        };

        updateProgress();
        window.addEventListener("scroll", updateProgress, { passive: true });
        window.addEventListener("resize", updateProgress);
    }

    /* ---------------------------------------------------------------
       5. MOBILE SLIDE MENU + OVERLAY
    ---------------------------------------------------------------- */
    function initMobileMenu() {
        const hamburger = $("#fgHamburgerBtn");
        const menu = $("#fgMobileMenu");
        const overlay = $("#fgMobileOverlay");

        // Keep a single source of truth for the mobile close control.
        // Remove any legacy drawer close control left by cached/older markup.
        $$("#fgMobileCloseBtn, .fg-mobile-close").forEach((control) => control.remove());

        if (!hamburger || !menu || !overlay) return;

        const openMenu = () => {
            menu.classList.add("fg-mobile-menu--open");
            overlay.classList.add("fg-mobile-overlay--visible");
            hamburger.classList.add("fg-hamburger--active");
            hamburger.setAttribute("aria-expanded", "true");
            hamburger.setAttribute("aria-label", "Close navigation menu");
            menu.setAttribute("aria-hidden", "false");
            document.body.classList.add("fg-no-scroll");
        };

        const closeMenu = () => {
            menu.classList.remove("fg-mobile-menu--open");
            overlay.classList.remove("fg-mobile-overlay--visible");
            hamburger.classList.remove("fg-hamburger--active");
            hamburger.setAttribute("aria-expanded", "false");
            hamburger.setAttribute("aria-label", "Open navigation menu");
            menu.setAttribute("aria-hidden", "true");
            document.body.classList.remove("fg-no-scroll");
        };

        hamburger.addEventListener("click", () => {
            const isOpen = menu.classList.contains("fg-mobile-menu--open");
            isOpen ? closeMenu() : openMenu();
        });

        overlay.addEventListener("click", closeMenu);

        // Close after choosing any destination in the mobile menu.
        $$("a", menu).forEach((link) => link.addEventListener("click", closeMenu));

        // Keep menu state sane when resizing from mobile to desktop.
        window.addEventListener("resize", () => {
            if (window.innerWidth >= 1024) closeMenu();
        }, { passive: true });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") closeMenu();
        });
    }

    /* ---------------------------------------------------------------
       6. MOBILE ACCORDION (Services / Government Schemes)
    ---------------------------------------------------------------- */
    function initMobileAccordion() {
        const toggles = $$(".fg-mobile-accordion__toggle");

        toggles.forEach((toggle) => {
            toggle.addEventListener("click", () => {
                const parent = toggle.closest(".fg-mobile-accordion");
                const isActive = parent.classList.contains("fg-mobile-accordion--active");

                $$(".fg-mobile-accordion--active").forEach((item) => {
                    if (item !== parent) item.classList.remove("fg-mobile-accordion--active");
                });

                parent.classList.toggle("fg-mobile-accordion--active", !isActive);
            });
        });
    }

    /* ---------------------------------------------------------------
       7. BACK TO TOP BUTTON
    ---------------------------------------------------------------- */
    function initBackToTop() {
        const btn = $("#fgBackToTop");
        if (!btn) return;

        const toggleVisibility = () => {
            btn.classList.toggle("fg-back-to-top--visible", window.scrollY > 400);
        };

        btn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });

        toggleVisibility();
        window.addEventListener("scroll", toggleVisibility, { passive: true });
    }

    /* ---------------------------------------------------------------
       8. SMOOTH SCROLL FOR ON-PAGE ANCHOR LINKS
    ---------------------------------------------------------------- */
    function initSmoothAnchorScroll() {
        document.addEventListener("click", (e) => {
            const link = e.target.closest('a[href*="#"]');
            if (!link) return;

            const url = new URL(link.href, window.location.href);
            if (url.pathname !== window.location.pathname || !url.hash) return;

            const target = document.querySelector(url.hash);
            if (!target) return;

            e.preventDefault();
            const headerOffset = 90;
            const targetPosition = target.getBoundingClientRect().top + window.scrollY - headerOffset;
            window.scrollTo({ top: targetPosition, behavior: "smooth" });
        });
    }

    /* ---------------------------------------------------------------
       9. NEWSLETTER FORM — DEMO SUBMIT HANDLER
       Wire this up to the real Django endpoint via fetch() + CSRF token.
    ---------------------------------------------------------------- */
    function initNewsletterForm() {
        const form = $("#fgNewsletterForm");
        if (!form) return;

        form.addEventListener("submit", (e) => {
            const emailInput = $('input[name="newsletter_email"]', form);

            if (!emailInput || emailInput.value.trim() === "") {
                e.preventDefault();
                showToast("Please enter a valid email address.", "error");
            }
        });
    }

    /* ---------------------------------------------------------------
       10. TOAST NOTIFICATION HELPER
       Usage: showToast("Message here", "success" | "error" | "info");
       Exposed on window so any page-level script can trigger a toast.
    ---------------------------------------------------------------- */
    function showToast(message, type = "info") {
        const container = $("#fgToastContainer");
        if (!container) return;

        const iconMap = {
            success: "fa-circle-check",
            error: "fa-circle-exclamation",
            info: "fa-circle-info"
        };

        const toastEl = document.createElement("div");
        toastEl.className = `fg-toast fg-toast--${type}`;
        toastEl.setAttribute("role", "alert");
        toastEl.innerHTML = `
            <i class="fa-solid ${iconMap[type] || iconMap.info}"></i>
            <span class="fg-toast__message"></span>
            <button type="button" class="fg-toast__close" aria-label="Close notification">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;
        toastEl.querySelector(".fg-toast__message").textContent = message;

        const removeToast = () => {
            toastEl.classList.add("fg-toast--hide");
            window.setTimeout(() => toastEl.remove(), 300);
        };

        toastEl.querySelector(".fg-toast__close").addEventListener("click", removeToast);
        container.appendChild(toastEl);
        window.setTimeout(removeToast, 5000);
    }

    window.fgShowToast = showToast;

    /* ---------------------------------------------------------------
       11. DJANGO MESSAGES
    ---------------------------------------------------------------- */
    function initDjangoMessages() {
        const holder = $("[data-fg-messages]");
        if (!holder) return;

        $$("[data-message]", holder).forEach((item) => {
            const tags = item.dataset.tags || "info";
            const type = tags.includes("success") ? "success" : tags.includes("error") ? "error" : "info";
            showToast(item.dataset.message || "", type);
        });
    }

    /* Prevent double submits and give slower network requests clear feedback. */
    function initFormFeedback() {
        $$('form[method="post"]').forEach((form) => {
            form.addEventListener("submit", () => {
                const button = form.querySelector('button[type="submit"]');
                if (!button || form.dataset.submitting === "true") return;
                form.dataset.submitting = "true";
                button.disabled = true;
                button.setAttribute("aria-busy", "true");
                const label = button.querySelector(".fg-btn-label");
                if (label) label.textContent = "Sending…";
                else button.dataset.originalText = button.textContent.trim();
            });
        });
    }

    /* ---------------------------------------------------------------
       12. COOKIE CONSENT
    ---------------------------------------------------------------- */
    function initCookieConsent() {
        const banner = $("#fgCookieConsent");
        if (!banner) return;

        const cookieName = "fg_cookie_consent";
        if (getCookie(cookieName)) return;

        const functional = $("#fgCookieFunctional");
        const analytics = $("#fgCookieAnalytics");
        const marketing = $("#fgCookieMarketing");

        const setConsent = (settings) => {
            const value = encodeURIComponent(JSON.stringify(settings));
            const expires = new Date();
            expires.setFullYear(expires.getFullYear() + 1);
            document.cookie = `${cookieName}=${value}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
            banner.classList.remove("fg-cookie-consent--visible");
            banner.setAttribute("aria-hidden", "true");
        };

        const selectedConsent = () => ({
            necessary: true,
            functional: Boolean(functional && functional.checked),
            analytics: Boolean(analytics && analytics.checked),
            marketing: Boolean(marketing && marketing.checked)
        });

        $("#fgCookieReject")?.addEventListener("click", () => {
            setConsent({ necessary: true, functional: false, analytics: false, marketing: false });
        });

        $("#fgCookieSave")?.addEventListener("click", () => {
            setConsent(selectedConsent());
        });

        $("#fgCookieAccept")?.addEventListener("click", () => {
            setConsent({ necessary: true, functional: true, analytics: true, marketing: true });
        });

        window.setTimeout(() => {
            banner.classList.add("fg-cookie-consent--visible");
            banner.setAttribute("aria-hidden", "false");
        }, 700);
    }

    function getCookie(name) {
        return document.cookie
            .split("; ")
            .find((row) => row.startsWith(`${name}=`))
            ?.split("=")[1];
    }

})();
