# Performance Report

## Applied

The project already uses deferred project JavaScript, static asset paths, responsive CSS, and database filtering. This audit added no speculative dependency or analytics changes. Dynamic sitemap generation now remains lightweight and safe.

## Deployment recommendations

Run `collectstatic`, enable WhiteNoise or Nginx compression and immutable static caching, convert oversized images to WebP/AVIF, preload only the actual LCP image/font, and validate Core Web Vitals with Lighthouse on mobile and desktop. A before/after Lighthouse score cannot be honestly reported without a reachable deployment.
