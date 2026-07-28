# Website design rules (condensed from Hallmark)

Concrete, checkable rules for writing website code that doesn't read as
generic AI output. Follow these when writing any HTML/CSS/React for a site.

## Hard rules

1. **No fabricated content.** Don't invent stats, testimonials, customer
   logos, or counts ("+47% conversion", "trusted by 50,000 teams"). If no
   real number was given, use a placeholder like "— metric to confirm" or
   skip that section entirely.
2. **No fake browser/OS chrome.** Don't hand-draw fake browser title bars,
   traffic-light dots, fake phone frames, or fake code-editor windows around
   content. Just show the content, or a real screenshot in a plain `<figure>`.
3. **No italic headings.** Headings/display text stay `font-style: normal`.
   Never italicize a heading or a word inside one for emphasis — use font
   weight or an accent color instead. Italics are fine in body copy only.
4. **Real design tokens, not scattered inline colors.** Define colors and
   fonts once (CSS variables / Tailwind theme), then reference them
   everywhere. Don't sprinkle random hex codes or `font-family` overrides
   through the markup.
5. **Mobile-first, genuinely responsive.** Must render cleanly at 320px,
   375px, 414px, and 768px widths — no horizontal scroll (`overflow-x: clip`
   on `html` and `body`, not `hidden`), no two-line-wrapping buttons/nav
   links, image grid columns use `minmax(0, 1fr)` not bare `1fr`.
6. **Avoid the generic AI look.** No default purple-to-pink gradient hero,
   no unexplained glassmorphism everywhere, no emoji used as icons (use real
   SVG icons — Heroicons/Lucide-style), no giant generic hero + 3 identical
   feature cards + testimonial carousel on every single page regardless of
   what the site is for. Vary section structure to fit the actual content.
7. **Interactive elements need real states.** Buttons/links/inputs should
   have visible hover, focus, and active states with smooth transitions
   (150-300ms) — not just a bare default browser style.
8. **Accessibility floor.** 4.5:1 text contrast minimum in light mode,
   visible focus outlines for keyboard nav, respect `prefers-reduced-motion`.

## Before calling a page done

- Does it actually look like it's about what the site is for, not a generic
  template with the topic swapped in?
- Read back your own CSS/markup: any of the anti-patterns above present?
  Fix them before finishing, don't ship a first draft with known issues.
