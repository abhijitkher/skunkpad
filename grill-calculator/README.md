# grill-calculator

**The Meat Oracle** — a single-page grilling calculator that divines how much meat to buy for a cookout, then suggests what to cook with it.

No build step, no dependencies. One self-contained `index.html`: markup, styles, SVG artwork, and logic all inline.

## What it does

You tell it who's coming and the rest follows:

- **The Gathering** — counts of men, women, and kids, each with an appetite slider (a nibble to full carnivore). Kids scale by age band, since a teen eats like an adult and a toddler doesn't.
- **The Offerings** — pick your meats (beef, pork, chicken, sausage, fish, shellfish). The total splits evenly across them.
- **The Flame** — charcoal, gas, smoker, or electric. This doesn't change how much people eat; it shapes the cooking tips and nudges the smoker number up for the long low-and-slow shrink.
- **Sides toggle** — trims the meat by a quarter when there's a real spread of sides.

Output is total **raw** pounds to buy, a per-meat breakdown rounded to the quarter pound, and a recipe suggestion per meat (low-and-slow cuts when a smoker is selected), each linking out to a recipe search.

## How the math works

Each eater gets a target of **cooked** edible meat (a regular man ~0.5 lb, a regular woman a bit less, a kid scaled by age), swung 60%–160% by the appetite slider. That cooked target is split across the chosen meats, then grossed up to raw buying weight using a per-meat yield factor that accounts for cooking shrink plus bone and shell waste. Shellfish needs the most raw weight (mostly shell); sausage the least. These are grill-day rules of thumb, not lab figures.

## Design

Styled as a mystic linocut broadside: a single dark ink tone printed on kraft paper, hand-drawn SVG artwork (an all-seeing eye radiating sunbeams) run through an SVG displacement filter so the edges break like carved block-print ink. Woodblock display type (Rye) over typewriter body (Special Elite).

## Run it

Open `index.html` in a browser. That's the whole thing.

## Deploy

Netlify, base directory `grill-calculator`, publish `.` — static, no build command. See `netlify.toml`.
